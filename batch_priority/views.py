from collections import defaultdict
from datetime import datetime, timedelta, date
import csv
import os
import markdown
from django.shortcuts import get_object_or_404, render, redirect
from django.db import models
from django.db.models import Count, Case, When, Value, IntegerField, Min, F
from django.db.models.functions import (
    Lower,
    TruncWeek,
    TruncDay,
    ExtractWeek,
)
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.http import JsonResponse
from .forms import (
    BatchForm,
    BayForm,
    CustomUserCreationForm,
    ProductForm,
    CommentForm,
    DailyDiscussionCommentForm,
)
from .models import (
    Bay,
    Batch,
    Product,
    TargetDate,
    DailyDiscussion,
    DailyDiscussionComment,
)
from .utils import get_week_range, get_start_date_of_week


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


def batch_search(request):
    query = request.GET.get("q")
    if query:
        results = Batch.objects.filter(batch_number__icontains=query)
    else:
        results = None
    return render(
        request, "batch/batch_search.html", {"results": results, "query": query}
    )


def schedule(request):
    selected_week = request.GET.get("week")
    if selected_week:
        selected_date = datetime.strptime(selected_week, "%Y-%m-%d")
    else:
        # If no week is selected, default to the current week
        selected_date = datetime.now()

    # Get the start and end dates of the selected week
    start_of_week, end_of_week = get_week_range(selected_date)
    week_commencing = start_of_week.strftime("%d-%m-%Y")

    # Filter batches with a manufacture date within the selected week
    batches = Batch.objects.filter(manufacture_date__range=[start_of_week, end_of_week])

    # Group batches by manufacture date
    calendar = defaultdict(list)
    for batch in batches:
        calendar[batch.manufacture_date.strftime("%d-%m-%Y")].append(batch)

    # Convert the dictionary to a list of tuples
    calendar = sorted(calendar.items())

    # Generate calendar days for the template
    calendar_days = [
        (start_of_week + timedelta(days=i)).strftime("%d-%m-%Y") for i in range(7)
    ]

    return render(
        request,
        "schedule/schedule.html",
        {
            "calendar": calendar,
            "selected_week": selected_date.strftime("%Y-%m-%d"),
            "week_commencing": week_commencing,
            "calendar_days": calendar_days,
        },
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
            selected_bays = request.POST.getlist("selected_bays")
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
                "start_date": (
                    target_date.target_start_date.strftime("%Y-%m-%d")
                    if target_date and target_date.target_start_date
                    else ""
                ),
                "end_date": (
                    target_date.target_end_date.strftime("%Y-%m-%d")
                    if target_date and target_date.target_end_date
                    else ""
                ),
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
    # Order batches by newest first
    batches = Batch.objects.order_by("-created_at")

    # Number of batches per page
    batches_per_page = 10
    paginator = Paginator(batches, batches_per_page)

    page = request.GET.get("page")
    try:
        batches = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        batches = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page of results.
        batches = paginator.page(paginator.num_pages)

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
    return render(request, "registration/signup.html", {"form": form})


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


def batches_per_user_per_week_data(request):
    # Fetch data for completed batches by user per week
    data = (
        Batch.objects.filter(batch_complete=True, batch_complete_date__isnull=False)
        .annotate(week=TruncWeek("batch_complete_date"))
        .values("completed_by", "week")
        .annotate(batch_count=Count("id"))
        .order_by("completed_by", "week")
    )

    # get data for the chart
    user_week_data = {}
    all_weeks = set()  # get all unique weeks
    for entry in data:
        user_id = entry["completed_by"]
        week = entry["week"].strftime("%d-%m-%Y")
        batch_count = entry["batch_count"]
        all_weeks.add(week)
        if user_id not in user_week_data:
            user_week_data[user_id] = {"labels": [], "data": []}
        user_week_data[user_id]["labels"].append(week)
        user_week_data[user_id]["data"].append(batch_count)

    # hacky way to add zeros to users who haven't completed batches
    for user_id, data in user_week_data.items():
        missing_weeks = all_weeks - set(data["labels"])
        for week in missing_weeks:
            data["labels"].append(week)
            data["data"].append(0)

        # sort labels and data based on week
        data["labels"], data["data"] = zip(*sorted(zip(data["labels"], data["data"])))

    # grab usernames
    user_mapping = {user.id: user.username for user in User.objects.all()}
    for user_id, data in user_week_data.items():
        username = user_mapping.get(user_id, "Unknown")
        data["username"] = username

    return JsonResponse({"user_week_data": user_week_data})


def batches_completed(request):
    return render(request, "reports/completed.html")


def team_leader_kpi(request):
    # Fetch all completed batches with week information and count per user
    team_leader_stats = (
        Batch.objects.filter(batch_complete=True)
        .annotate(week=ExtractWeek("batch_complete_date"))
        .values("completed_by", "week")
        .annotate(batches_completed=Count("id"))
        .order_by("week")
    )

    # Group stats by week
    stats_by_week = defaultdict(list)
    for stat in team_leader_stats:
        stats_by_week[stat["week"]].append(stat)

    stats_by_week = dict(sorted(stats_by_week.items(), reverse=True))

    # Fetch usernames for each user ID
    user_ids = set(stat["completed_by"] for stat in team_leader_stats)
    users = User.objects.filter(id__in=user_ids)
    user_mapping = {user.id: user.username for user in users}

    # Organize stats by week and add username and batch details
    team_leader_stats_grouped = []
    for week, stats in stats_by_week.items():
        week_start_date = get_start_date_of_week(
            2024, week
        )  # Assuming 2024 as the year
        week_data = {"week_start_date": week_start_date, "stats": []}
        for stat in stats:
            user_id = stat["completed_by"]
            username = user_mapping.get(user_id, "Unknown")
            stat["username"] = username

            # Fetch batch details for the user in the week
            week_batches = Batch.objects.filter(
                batch_complete=True,
                completed_by=user_id,
                batch_complete_date__week=week,
            ).values("batch_number", "batch_complete_date", "id")

            # Add batch details to the stat
            stat["week_batches"] = week_batches

            week_data["stats"].append(stat)

        team_leader_stats_grouped.append(week_data)

    return render(
        request,
        "reports/team_leader_kpi.html",
        {"team_leader_stats_grouped": team_leader_stats_grouped},
    )


def daily_discussion(request, date=None):
    if date is None:
        date = timezone.now().date()
    else:
        date = datetime.strptime(date, "%Y-%m-%d").date()

    discussion, created = DailyDiscussion.objects.get_or_create(date=date)

    # Fetch batches completed on the specified date
    batches_completed_on_date = Batch.objects.filter(
        batch_complete=True, batch_complete_date__date=date
    )

    if request.method == "POST":
        form = DailyDiscussionCommentForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text"]
            user = request.user if request.user.is_authenticated else None
            comment = DailyDiscussionComment.objects.create(
                discussion=discussion, user=user, text=text
            )

            return redirect("daily_discussion", date=date)
    else:
        form = DailyDiscussionCommentForm()

    return render(
        request,
        "kpi/daily_discussion.html",
        {
            "discussion": discussion,
            "form": form,
            "batches_completed_on_date": batches_completed_on_date,
        },
    )


def edit_discussion_comment(request, comment_id):
    # Fetch the comment by its ID
    comment = get_object_or_404(DailyDiscussionComment, id=comment_id)

    # Check if the current user is the owner of the comment
    if request.user != comment.user:
        return redirect("daily_discussion")

    if request.method == "POST":
        form = DailyDiscussionCommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect("daily_discussion", date=comment.discussion.date)
    else:
        form = DailyDiscussionCommentForm(instance=comment)

    return render(
        request, "kpi/edit_discussion_comment.html", {"form": form, "comment": comment}
    )


def changelog(request):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    changelog_file_path = os.path.join(base_dir, "..", "CHANGELOG.md")

    try:
        with open(changelog_file_path, "r") as changelog_file:
            changelog_content = changelog_file.read()
            html = markdown.markdown(changelog_content)
    except FileNotFoundError:
        changelog_content = "Changelog not found."

    return render(request, "changelog.html", {"changelog_content": html})


class WIPQueueView(TemplateView):
    template_name = "schedule/wip_queue.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        batches = Batch.objects.filter(batch_complete=False).order_by(
            "manufacture_date"
        )
        wip_queue = []
        for batch in batches:
            working_days_since_manufacture = self.calculate_working_days(
                batch.manufacture_date
            )
            if working_days_since_manufacture is None:
                working_days_since_manufacture = "Production Scheduled"
            elif working_days_since_manufacture == 0:
                working_days_since_manufacture = "Today"
            elif working_days_since_manufacture == 1:
                working_days_since_manufacture = "Yesterday"
            else:
                working_days_since_manufacture = (
                    f"{working_days_since_manufacture} days"
                )
            wip_queue.append(
                {
                    "batch_id": batch.id,
                    "batch_number": batch.batch_number,
                    "product_code": batch.product_code,
                    "product": batch.product_code.product,
                    "manufacture_date": batch.manufacture_date,
                    "working_days_since_manufacture": working_days_since_manufacture,
                    "on_hold": "Yes" if batch.on_hold else "No",
                }
            )
        context["wip_queue"] = wip_queue
        return context

    def calculate_working_days(self, manufacture_date):
        if not manufacture_date:
            return None
        today = date.today()
        if manufacture_date <= today:
            delta = today - manufacture_date
            num_working_days = 0
            for i in range(delta.days):
                current_date = manufacture_date + timedelta(days=i)
                if current_date.weekday() < 5:  # Monday to Friday (0 to 4)
                    num_working_days += 1
            return num_working_days
        else:
            return None
