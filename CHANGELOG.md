# Changelog

## [Feb 17, 2024]
- add: ability to edit target dates using a modal view

## [Feb 17, 2024]
- tidy: ability to hide / add bays when adding batch
- add: kpi view for batches completed per week by users

## [Feb 15, 2024]
- add: schedule view for W.I.P queue
- fix: remove bay requirement when adding batches
- add: search batches

## [Feb 14, 2024]
- fix: batch number not rendering if user is logged out
- add: add schedule to see batches planned for manufacture in a given timeframe

## [Feb 3, 2024]
- add: ability to edit comments on daily_discussion
- add: add links to daily_discussion - yesterday / today and tomorrows discussions
- add: changelog view

## [Feb 2, 2024]
- add: daily discussion on completed batches
- fix: week now starts from the first Monday of each week, not the first batch completed in that week
- add: reports page for completed batches per week by user/team leader
- add: password reset, change password, and support for email backend


## [Jan 31, 2024]
- fix: comments when generating
- add: pagination to locations page
- add: command to create bays based on the .env file
- add: command to generate random batches
- fix: error on load if username not in db
- add: allow team leaders to add batches
- fix: user details not saving on initial batch creation if production or complete is checked
- refactor: Add grid mobile support
- add: management command to auto-create user groups

## [Jan 30, 2024]
- add: new report, batches completed before target dates
- add: presentation to sample list
- add: counter to batch list, small pill, and color bg to BOM received
- amend Unknown to System

## [Jan 29, 2024]
- add: user menu
- fix: URL redirection on success of login
- cleanup
- add: @domain.com requirement to signup
- add: comments to admin
- add: only manager has access to add batches/bays/products
- fix: update links to batch detail instead of batch edit
- add: assigned to
- add: assigned to for production checks, 
- fix: bug where production check and batch complete dates were being overwritten on edits
- fix: production check and completed by user not saving

## [Jan 27, 2024]
- add: move on hold batches to the end of the list
- fix: hide notes if empty
- fix: remove None returning on empty fields
- fix: remove 'bay' before bay titles
- fix product list reference
- fix: stop rendering None if empty
- fix: hide notes if empty
- fix: batch link goes to batch detail instead of edit
- fix: hide batch notes if empty, 
- tidy batch complete date if statement
- fix: empty notes returning None
- fix: old vs new correct order
- add: hide batch location URL if not logged in
- refactor: Add mobile styling support
- add: mobile styling support
- add: grid mobile support

## [Jan 26, 2024]
- add: remove inactive batches with target dates that are set as inactive

## [Jan 21, 2024]
- add: env step to readme
- fix: static files
- fix: target date history, no more deleting the whole row and losing history if unchecked
- fix: remove unused import
- add: better audit logs
- add: location history (locations view)
- fix: updating target dates on save even when nothing's changed

## [Jan 18, 2024]
- add: locations (location view)
- add: date of manufacture to Batch
- fix: completed on view
- add: completed batches per week graph (batches_completed)
- add: view to see batches completed per week (batches_completed)

## [Jan 17, 2024]
- add: completed batches per week graph (batches_completed)
- add: view to see batches that have been completed on certain dates, can filter by date range (CompletedOnView)
- add: add comments to batch
- add: add batch detail view
- add: add readme
- add: hide on hold from warehouse - warehouse_list view
- add: complete date and username to prod check view, if target date is before todays date then colour cell in red
- add: add on hold to Batch
- add: add batch history
- add: add production check target to Batch
- add: add created by and last modified by fields to Batch

## [Jan 15, 2024]
- add: added audit logs
- add: added production checks - if batch_complete = Complete, production_check = False

## [Jan 15, 2024]
- add: added sampling views - if samples_received = False display batch

## [Jan 14, 2024]
- initial project build and commit to github