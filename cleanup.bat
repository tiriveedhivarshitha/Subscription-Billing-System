@echo off
echo ============================================
echo   milestone2 — Full Cleanup
echo ============================================
echo.

set ROOT=C:\Users\tiruv\Desktop\milestone2

REM ======= BACKEND FOLDER =======
echo [Backend folder]
for %%f in (
  check_inv.py check_schemas.py check_schemas2.py check_sub_time.py
  fix_db.py fix_db2.py fix_main.py fix_plan_features.py fix_subtotal.py fix.py
  insert_demo_invoices.py insert_demo_invoices2.py
  insert_data.py insert_more_data.py insert_payments.py insert_recurring.py insert_trial_data.py
  run_insert.py update_htmls.py patch_admin.py
  seed_audit.py seed_more_plans.py seed_netflix.py seed_plans.py
  temp_check_audit.py temp_check_audit_schema.py temp_check_audit2.py temp_schema.py temp_schema2.py
  test_all.py test_api_queries.py test_billing.py test_failed.py test_inv.py test_inv2.py
  test_monthly.py test_pdf.py test_plans.py test_req.py test_req2.py test_unpaid.py
  test_change.py test_load.py test_post.py
) do (
  if exist "%ROOT%\Backend\%%f" (
    del /f /q "%ROOT%\Backend\%%f"
    echo   Deleted: %%f
  )
)
del /f /q "%ROOT%\Backend\INV-*.pdf" 2>nul

REM ======= FRONTEND FOLDER =======
echo.
echo [Frontend folder]
for %%f in (
  check_js.py check_te.py
  clean_dashboard_html.py clean_js.py clean_js2.py clean_other_html.py
  fix.py fix_audit.py fix_audit_url.py fix_encoding.py fix_everything.py
  fix_html.py fix_html_again.py fix_invoice_js.py fix_pdf.py fix_sidebar.py fix_utf8_crisis.py
  fix_js_refunds.py fix_js_sidebar.py fix_marks.py fix_monthly_chart.py
  fix_pdf_backend.py fix_pdf_frontend.py fix_pie.py fix_plans_js.py fix_summary.py fix_whitespace.py
  update_all_js_i18n.py update_audit_html_i18n.py update_audit_js_i18n.py
  update_html_charts.py update_html_i18n.py update_html_kpi_i18n.py
  update_js_charts.py update_js_i18n.py update_js_kpi_i18n.py
  update_more_html_i18n.py verify_crisis.py
  dashboard.html dashboard.js
) do (
  if exist "%ROOT%\frontend\%%f" (
    del /f /q "%ROOT%\frontend\%%f"
    echo   Deleted: %%f
  )
)

REM ======= ROOT FOLDER =======
echo.
echo [Root folder]
for %%f in (
  fix_*.py test_*.py seed_*.py temp_*.py insert_*.py check_*.py clean_*.py update_*.py
  run_insert.py update_htmls.py patch_admin.py insert_data.sql
) do (
  if exist "%ROOT%\%%f" (
    del /f /q "%ROOT%\%%f"
    echo   Deleted: %%f
  )
)

echo.
echo ============================================
echo   Done! Now delete cleanup.bat itself too.
echo ============================================
pause
