import re
with open("dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

sidebar = """    <div class="sidebar">
        <h3 style="text-align: center;" data-i18n="billing_platform">Billing Platform</h3>
        
        <div style="text-align: center; margin-bottom: 15px;">
            <select id="langSelect" onchange="changeLanguage()" style="padding: 5px; width: 80%; background: #444; color: white; border: 1px solid #666;">
                <option value="en">English</option>
                <option value="te">Telugu</option>
                <option value="hi">Hindi</option>
                <option value="ta">Tamil</option>
                <option value="kn">Kannada</option>
            </select>
        </div>

        <div style="background: #222; padding: 5px 15px; margin-top: 10px; font-size: 12px; color: #888;" data-i18n="admin_portal">--- ADMIN PORTAL ---</div>
        <a onclick="showSection('metrics')" style="background:#444; font-weight:bold;" data-i18n="admin_metrics">Admin Metrics</a>
        <a onclick="showSection('failed_payments')" style="background:#444; font-weight:bold;" data-i18n="failed_payments">Failed Payments</a>
        <a onclick="showSection('audit_logs')" style="background:#444; font-weight:bold;" data-i18n="audit_logs">Audit Logs</a>
        
        <div style="background: #222; padding: 5px 15px; margin-top: 20px; font-size: 12px; color: #888;" data-i18n="customer_portal">--- CUSTOMER PORTAL ---</div>
        <a onclick="showSection('plan_cards')" style="background:#0056b3; font-weight:bold;" data-i18n="browse_plans">Browse Plans</a>
        <a onclick="showSection('invoices')" data-i18n="my_invoices">My Invoices</a>
        <a onclick="showSection('upgrade')" data-i18n="change_plan">Change Plan</a>
        <a onclick="showSection('payments')" data-i18n="pay_invoice">Pay Invoice</a>
        <a onclick="showSection('refunds')" data-i18n="refunds">Refunds</a>
        
        <a onclick="logout()" style="color: #ff6666; margin-top: 30px;" data-i18n="logout">Logout</a>
    </div>"""

html = re.sub(r'<div class="sidebar">[\s\S]*?</div>', sidebar, html)

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
