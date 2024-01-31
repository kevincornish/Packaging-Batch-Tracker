import csv
from django.shortcuts import get_object_or_404, render, redirect
from django.db import models
from django.db.models import Count, Case, When, Value, IntegerField, Min, F
from django.db.models.functions import Lower, TruncWeek, TruncDay
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from .forms import BatchForm, BayForm, CustomUserCreationForm, ProductForm, CommentForm
from .models import Bay, Batch, Product, TargetDate


def batch_list(request):
    bays = (
        Bay.objects.annotate(
            total_batches=Count("targetdate__batch"),
            completed_batches=Count(
                Case(
                    When(targetdate__batch__batch_complete=True, then=1),
                    output_field=IntegerField(),
                )
            ),
        )
        .exclude(completed_batches=Count("targetdate__batch"))
        .prefetch_related("targetdate_set__batch")
        .order_by("name")
    )
    today_date = timezone.now().date()

    for bay in bays:
        # Exclude batches with inactive target dates
        active_batches = bay.targetdate_set.filter(is_active=True).exclude(
            batch__batch_complete=True
        )
        on_hold_batches = active_batches.filter(batch__on_hold=True)
        normal_batches = active_batches.exclude(batch__on_hold=True)

        # Order normal batches by earliest target date and stick the batches on hold at the end of the list
        ordered_normal_batches = normal_batches.annotate(
            earliest_target_date=Min("target_start_date")
        ).order_by("earliest_target_date")
        bay.active_batches = list(ordered_normal_batches) + list(on_hold_batches)

    return render(
        request, "batch/batch_list.html", {"bays": bays, "today_date": today_date}
    )


def warehouse_list(request):
    batches = (
        Batch.objects.filter(bom_received=False, batch_complete=False, on_hold=False)
        .annotate(earliest_start_date=Min("targetdate__target_start_date"))
        .order_by("earliest_start_date")
    )

    earliest_date = batches.first().earliest_start_date if batches else None

    return render(
        request,
        "reports/warehouse_list.html",
        {"batches": batches, "earliest_date": earliest_date},
    )


def samples_list(request):
    batches = Batch.objects.filter(
        samples_received=False, batch_complete=False
    ).order_by("complete_date_target")
    return render(request, "reports/samples_list.html", {"batches": batches})


def production_check_list(request):
    batches = Batch.objects.filter(
        batch_complete=True, production_check=False
    ).order_by("complete_date_target")
    today_date = timezone.now().date()
    for batch in batches:
        batch.production_check_target = batch.batch_complete_date + timezone.timedelta(
            days=1
        )
    return render(
        request,
        "reports/production_checks.html",
        {"batches": batches, "today_date": today_date},
    )


def archive_list(request):
    batches = Batch.objects.filter(batch_complete=True, production_check=True).order_by(
        "production_check_date"
    )
    return render(request, "reports/archive.html", {"batches": batches})


@login_required
def add_batch(request):
    bays = Bay.objects.all()

    if request.method == "POST":
        form = BatchForm(request.POST)
        if form.is_valid():
            # Check if at least one bay is selected
            selected_bays = request.POST.getlist("selected_bays")
            if not selected_bays:
                form.add_error(None, ValidationError("Please select at least one bay."))
                return render(
                    request, "batch/add_batch.html", {"form": form, "bays": bays}
                )
            batch_instance = form.save(commit=False, created_by=request.user)
            batch_instance.user = request.user
            batch_instance.save()
            for bay_id in selected_bays:
                bay = get_object_or_404(Bay, id=bay_id)
                start_date = request.POST.get(f"start_date_{bay_id}")
                end_date = request.POST.get(f"end_date_{bay_id}")
                try:
                    target_start_date = parse_date(start_date)
                    target_end_date = parse_date(end_date) if end_date else None
                except (ValueError, TypeError):
                    form.add_error(
                        None,
                        ValidationError("Invalid date format. Use YYYY-MM-DD format."),
                    )
                    return render(
                        request, "batch/add_batch.html", {"form": form, "bays": bays}
                    )

                TargetDate.objects.create(
                    batch=batch_instance,
                    bay=bay,
                    target_start_date=target_start_date,
                    target_end_date=target_end_date,
                )
            return redirect("batch_list")
        else:
            return render(request, "batch/add_batch.html", {"form": form, "bays": bays})
    else:
        form = BatchForm()
    if form.errors:
        return render(request, "batch/add_batch.html", {"form": form, "bays": bays})

    return render(request, "batch/add_batch.html", {"form": form, "bays": bays})


@login_required
def edit_batch(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)

    if request.method == "POST":
        form = BatchForm(request.POST, instance=batch)
        if form.is_valid():
            form.save(commit=False)
            batch.user = request.user
            form.save()

            selected_bays = request.POST.getlist("selected_bays")
            for bay_id in selected_bays:
                bay = get_object_or_404(Bay, id=bay_id)
                start_date = request.POST.get(f"start_date_{bay_id}")
                end_date = request.POST.get(f"end_date_{bay_id}")

                # Check if the dates have changed before updating or creating
                target_date, created = TargetDate.objects.get_or_create(
                    batch=batch,
                    bay=bay,
                    defaults={
                        "target_start_date": start_date,
                        "target_end_date": end_date,
                    },
                )

                if not created:
                    # If the TargetDate already existed, update the dates if they are different
                    if str(target_date.target_start_date) != str(start_date) or str(
                        target_date.target_end_date
                    ) != str(end_date):
                        target_date.target_start_date = start_date
                        target_date.target_end_date = end_date
                        target_date.is_active = True
                        target_date.save()

            # Mark current dates as inactive for unchecked bays
            unchecked_bays = Bay.objects.exclude(id__in=selected_bays)
            TargetDate.objects.filter(batch=batch, bay__in=unchecked_bays).update(
                is_active=False
            )

            return redirect("batch_list")
    else:
        form = BatchForm(instance=batch)

        bays = Bay.objects.all()

        existing_target_dates = TargetDate.objects.filter(batch=batch, is_active=True)
        existing_target_dates_dict = {
            target_date.bay_id: target_date for target_date in existing_target_dates
        }

        bay_data = []
        for bay in bays:
            target_date = existing_target_dates_dict.get(bay.id)
            bay_row = {
                "bay": bay,
                "selected": target_date is not None,
                "start_date": target_date.target_start_date.strftime("%Y-%m-%d")
                if target_date and target_date.target_start_date
                else "",
                "end_date": target_date.target_end_date.strftime("%Y-%m-%d")
                if target_date and target_date.target_end_date
                else "",
            }
            bay_data.append(bay_row)

        return render(
            request,
            "batch/edit_batch.html",
            {"form": form, "batch": batch, "bays": bay_data},
        )


def batch_detail(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    comments = batch.comments.all()

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.batch = batch
            new_comment.user = request.user if request.user.is_authenticated else None
            new_comment.save()
            comment_form = CommentForm()  # Reset the form after saving

    else:
        comment_form = CommentForm()

    return render(
        request,
        "batch/batch_detail.html",
        {"batch": batch, "comments": comments, "comment_form": comment_form},
    )


def batch_history(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    history_records = batch.history.all()

    changes = []

    for i in range(len(history_records) - 1, 0, -1):
        new_record, old_record = history_records[i], history_records[i - 1]
        delta = new_record.diff_against(old_record)

        for change in delta.changes:
            if change.field == "product_code":
                # Customize display for the product_code field
                old_product_code = Product.objects.get(id=change.old).product_code
                new_product_code = Product.objects.get(id=change.new).product_code
            else:
                # For other fields, use the default display values
                old_product_code = change.old
                new_product_code = change.new
            # Check if history_user is not None before accessing username
            history_user = new_record.last_modified_by
            username = history_user.username if history_user else "System"
            changes.append(
                {
                    "field": change.field,
                    "old": new_product_code,  # flip old and new - appears to be in reverse?
                    "new": old_product_code,
                    "user": username,
                    "timestamp": new_record.last_modified_at,
                }
            )

    # Reverse the order to display the latest changes first
    changes.reverse()

    context = {"batch": batch, "changes": changes}
    return render(request, "batch/batch_history.html", context)


@login_required
def locations(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    bays_assigned = TargetDate.objects.filter(batch=batch)

    changes = []

    for bay in bays_assigned:
        target_date_records = bay.history.all()

        # Check if there are records before iterating
        if target_date_records:
            # Include the initial created row if it has the necessary fields
            for i in range(len(target_date_records)):
                initial_record = target_date_records[i]
                username = (
                    initial_record.history_user.username
                    if initial_record.history_user
                    else "System"
                )
                changes.append(
                    {
                        "batch": batch.batch_number,
                        "field": "targetdate",
                        "bay": initial_record.bay,
                        "start_date": initial_record.target_start_date,
                        "end_date": initial_record.target_end_date,
                        "user": username,
                        "timestamp": initial_record.history_date,
                    }
                )
        # Sort changes by timestamp
    changes.sort(key=lambda x: x["timestamp"], reverse=True)

    context = {"batch": batch, "changes": changes}
    return render(request, "batch/batch_locations.html", context)


def location(request):
    batches = Batch.objects.all()
    return render(request, "batch/batches.html", {"batches": batches})


def bay_list(request):
    bays = Bay.objects.all()
    return render(request, "bay/bay_list.html", {"bays": bays})


@login_required
def add_bay(request):
    if request.method == "POST":
        form = BayForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("bay_list")
        else:
            return redirect("bay_list")
    else:
        form = BayForm()

    return render(request, "bay/add_bay.html", {"form": form})


@login_required
def edit_bay(request, bay_id):
    bay = get_object_or_404(Bay, id=bay_id)

    if request.method == "POST":
        form = BayForm(request.POST, instance=bay)
        if form.is_valid():
            form.save()
            return redirect("bay_list")
        else:
            return redirect("bay_list")
    else:
        form = BayForm(instance=bay)

    return render(request, "bay/edit_bay.html", {"form": form, "bay": bay})


@login_required
def product_list(request):
    products = Product.objects.annotate(
        presentation_lower=Case(
            When(
                product__exact="", then=Value("")
            ),  # Handle empty product field if needed
            default=Lower("presentation"),
            output_field=models.CharField(),
        )
    ).order_by("presentation_lower", "product_code")

    return render(request, "product/product_list.html", {"products": products})


@login_required
@csrf_exempt
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("product_list")
        else:
            return redirect("product_list")
    else:
        form = ProductForm()

    return render(request, "product/add_product.html", {"form": form})


@login_required
def import_products(request):
    if request.method == "POST" and request.FILES["csv_file"]:
        csv_file = request.FILES["csv_file"].read().decode("utf-8").splitlines()
        csv_reader = csv.reader(csv_file)

        header = next(csv_reader)
        header = [col.strip("\ufeff") for col in header]

        product_code_index = header.index("Product Code")
        product_description_index = header.index("Product Description")
        product_volume_index = header.index("Product Volume")

        for row in csv_reader:
            product_code = row[product_code_index]
            product_description = row[product_description_index]
            product_volume = row[product_volume_index]

            product_description = product_description.strip()
            existing_product = Product.objects.filter(product_code=product_code).first()

            if existing_product:
                existing_product.product = product_description
                existing_product.presentation = product_volume
                existing_product.save()
            else:
                Product.objects.create(
                    product_code=product_code,
                    product=product_description,
                    presentation=product_volume,
                )

        return redirect("product_list")

    return render(request, "product/import_products.html")


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("product_list")
        else:
            return redirect("product_list")
    else:
        form = ProductForm(instance=product)

    return render(
        request, "product/edit_product.html", {"form": form, "product": product}
    )


def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("batch_list")
    else:
        form = CustomUserCreationForm()
    return render(request, "user/signup.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get("next", "batch_list") or "batch_list"
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, "user/login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("batch_list")


class CompletedOnView(View):
    template_name = "batch/completed_on.html"

    def get(self, request, *args, **kwargs):
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        if start_date and end_date:
            batches = Batch.objects.filter(
                batch_complete_date__range=[start_date, end_date]
            )
        else:
            batches = Batch.objects.filter(batch_complete=True)

        return render(request, self.template_name, {"batches": batches})


def batches_per_week_data(request):
    data = (
        Batch.objects.filter(batch_complete=True, batch_complete_date__isnull=False)
        .annotate(week=TruncWeek("batch_complete_date"))
        .values("week")
        .annotate(batch_count=Count("id"))
        .order_by("week")
    )

    labels = [entry["week"].strftime("%d-%m-%Y") for entry in data]
    batch_counts = [entry["batch_count"] for entry in data]

    return JsonResponse({"labels": labels, "data": batch_counts})


def batches_per_day_data(request):
    data = (
        Batch.objects.filter(batch_complete=True, batch_complete_date__isnull=False)
        .annotate(day=TruncDay("batch_complete_date"))
        .values("day")
        .annotate(batch_count=Count("id"))
        .order_by("day")
    )

    labels = [entry["day"].strftime("%d-%m-%Y") for entry in data]
    batch_counts = [entry["batch_count"] for entry in data]

    return JsonResponse({"labels": labels, "data": batch_counts})


def batches_completed_before_target_data(request):
    data = (
        Batch.objects.filter(batch_complete=True, batch_complete_date__isnull=False)
        .annotate(
            week=TruncWeek("batch_complete_date"),
            completed_before_target=Count(
                Case(
                    When(batch_complete_date__lt=F("complete_date_target"), then=1),
                    output_field=IntegerField(),
                )
            ),
        )
        .values("week")
        .annotate(
            batch_count=Count("id"),
            completed_before_target_count=Count(
                Case(
                    When(batch_complete_date__lt=F("complete_date_target"), then=1),
                    output_field=IntegerField(),
                )
            ),
        )
        .order_by("week")
    )

    labels = [entry["week"].strftime("%d-%m-%Y") for entry in data]
    batch_counts = [entry["batch_count"] for entry in data]
    completed_before_target_counts = [
        entry["completed_before_target_count"] for entry in data
    ]

    return JsonResponse(
        {
            "labels": labels,
            "data": batch_counts,
            "completed_before_target_counts": completed_before_target_counts,
        }
    )


def batches_completed(request):
    return render(request, "reports/completed.html")
