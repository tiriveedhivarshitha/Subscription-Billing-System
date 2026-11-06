import json

js_code = """
const BASE_URL = "http://127.0.0.1:8000";
const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "index.html";
}

// TRANSLATION LOGIC
const translations = {
    en: {
        billing_platform: "Billing Platform", admin_portal: "--- ADMIN PORTAL ---", admin_metrics: "Admin Metrics",
        failed_payments: "Failed Payments", audit_logs: "Audit Logs", customer_portal: "--- CUSTOMER PORTAL ---",
        browse_plans: "Browse Plans", my_invoices: "My Invoices", change_plan: "Change Plan",
        pay_invoice: "Pay Invoice", refunds: "Refunds", logout: "Logout"
    },
    te: {
        billing_platform: "\u0c2c\u0c3f\u0c32\u0c4d\u0c32\u0c3f\u0c02\u0c17\u0c4d \u0c2a\u0c4d\u0c32\u0c3e\u0c1f\u0c4d\u0c2b\u0c3e\u0c30\u0c2e\u0c4d",
        admin_portal: "--- \u0c05\u0c21\u0c4d\u0c2e\u0c3f\u0c28\u0c4d \u0c2a\u0c4b\u0c30\u0c4d\u0c1f\u0c32\u0c4d ---",
        admin_metrics: "\u0c05\u0c21\u0c4d\u0c2e\u0c3f\u0c28\u0c4d \u0c2e\u0c46\u0c1f\u0c4d\u0c30\u0c3f\u0c15\u0c4d\u0c38\u0c4d",
        failed_payments: "\u0c35\u0c3f\u0c2b\u0c32\u0c2e\u0c48\u0c28 \u0c1a\u0c46\u0c32\u0c4d\u0c32\u0c3f\u0c02\u0c2a\u0c41\u0c32\u0c41",
        audit_logs: "\u0c06\u0c21\u0c3f\u0c1f\u0c4d \u0c32\u0c3e\u0c17\u0c4d\u0c38\u0c4d",
        customer_portal: "--- \u0c15\u0c38\u0c4d\u0c1f\u0c2e\u0c30\u0c4d \u0c2a\u0c4b\u0c30\u0c4d\u0c1f\u0c32\u0c4d ---",
        browse_plans: "\u0c2a\u0c4d\u0c32\u0c3e\u0c28\u0c4d\u0c32\u0c28\u0c41 \u0c2c\u0c4d\u0c30\u0c4c\u0c1c\u0c4d \u0c1a\u0c47\u0c2f\u0c02\u0c21\u0c3f",
        my_invoices: "\u0c28\u0c3e \u0c07\u0c28\u0c4d\u0c35\u0c3e\u0c2f\u0c3f\u0c38\u0c4d\u0c32\u0c41",
        change_plan: "\u0c2a\u0c4d\u0c32\u0c3e\u0c28\u0c4d \u0c2e\u0c3e\u0c30\u0c4d\u0c1a\u0c02\u0c21\u0c3f",
        pay_invoice: "\u0c07\u0c28\u0c4d\u0c35\u0c3e\u0c2f\u0c3f\u0c38\u0c4d \u0c1a\u0c46\u0c32\u0c4d\u0c32\u0c3f\u0c02\u0c1a\u0c02\u0c21\u0c3f",
        refunds: "\u0c35\u0c3e\u0c2a\u0c38\u0c41",
        logout: "\u0c32\u0c3e\u0c17\u0c4d \u0c05\u0c35\u0c41\u0c1f\u0c4d"
    },
    hi: {
        billing_platform: "\u092c\u093f\u0932\u093f\u0902\u0917 \u092a\u094d\u0932\u0947\u091f\u092b\u0949\u0930\u094d\u092e",
        admin_portal: "--- \u090f\u0921\u092e\u093f\u0928 \u092a\u094b\u0930\u094d\u091f\u0932 ---",
        admin_metrics: "\u090f\u0921\u092e\u093f\u0928 \u092e\u0947\u091f\u094d\u0930\u093f\u0915\u094d\u0938",
        failed_payments: "\u0935\u093f\u092b\u0932 \u092d\u0941\u0917\u0924\u093e\u0928",
        audit_logs: "\u0911\u0921\u093f\u091f \u0932\u0949\u0917",
        customer_portal: "--- \u0917\u094d\u0930\u093e\u0939\u0915 \u092a\u094b\u0930\u094d\u091f\u0932 ---",
        browse_plans: "\u092f\u094b\u091c\u0928\u093e\u090f\u0902 \u092c\u094d\u0930\u093e\u0909\u091c\u093c \u0915\u0930\u0947\u0902",
        my_invoices: "\u092e\u0947\u0930\u0947 \u091a\u093e\u0932\u093e\u0928",
        change_plan: "\u092f\u094b\u091c\u0928\u093e \u092c\u0926\u0932\u0947\u0902",
        pay_invoice: "\u091a\u093e\u0932\u093e\u0928 \u0915\u093e \u092d\u0941\u0917\u0924\u093e\u0928 \u0915\u0930\u0947\u0902",
        refunds: "\u0930\u093f\u092b\u0902\u0921",
        logout: "\u0932\u0949\u0917 \u0906\u0909\u091f"
    },
    ta: {
        billing_platform: "\u0baa\u0bbf\u0bb2\u0bcd\u0bb2\u0bbf\u0b99\u0bcd \u0ba4\u0bb3\u0bae\u0bcd",
        admin_portal: "--- \u0ba8\u0bbf\u0bb0\u0bcd\u0bb5\u0bbe\u0b95 \u0baa\u0bcb\u0bb0\u0bcd\u0b9f\u0bcd\u0b9f\u0bb2\u0bcd ---",
        admin_metrics: "\u0ba8\u0bbf\u0bb0\u0bcd\u0bb5\u0bbe\u0b95 \u0b85\u0bb3\u0bb5\u0bc0\u0b9f\u0bc1\u0b95\u0bb3\u0bcd",
        failed_payments: "\u0ba4\u0bcb\u0bb2\u0bcd\u0bb5\u0bbf\u0baf\u0b9f\u0bc8\u0ba8\u0bcd\u0ba4 \u0b95\u0bca\u0b9f\u0bc1\u0baa\u0bcd\u0baa\u0ba9\u0bb5\u0bc1\u0b95\u0bb3\u0bcd",
        audit_logs: "\u0ba4\u0ba3\u0bbf\u0b95\u0bcd\u0b95\u0bc8 \u0baa\u0ba4\u0bbf\u0bb5\u0bc1\u0b95\u0bb3\u0bcd",
        customer_portal: "--- \u0bb5\u0bbe\u0b9f\u0bbf\u0b95\u0bcd\u0b95\u0bc8\u0baf\u0bbe\u0bb3\u0bb0\u0bcd \u0baa\u0bcb\u0bb0\u0bcd\u0b9f\u0bcd\u0b9f\u0bb2\u0bcd ---",
        browse_plans: "\u0ba4\u0bbf\u0b9f\u0bcd\u0b9f\u0b99\u0bcd\u0b95\u0bb3\u0bc8 \u0b89\u0bb2\u0bbe\u0bb5\u0bc1",
        my_invoices: "\u0b8e\u0ba9\u0bcd \u0b87\u0ba9\u0bcd\u0bb5\u0bbe\u0baf\u0bcd\u0bb8\u0bcd\u0b95\u0bb3\u0bcd",
        change_plan: "\u0ba4\u0bbf\u0b9f\u0bcd\u0b9f\u0ba4\u0bcd\u0ba4\u0bc8 \u0bae\u0bbe\u0bb1\u0bcd\u0bb1\u0bc1",
        pay_invoice: "\u0b87\u0ba9\u0bcd\u0bb5\u0bbe\u0baf\u0bcd\u0bb8\u0bcd \u0b9a\u0bc6\u0bb2\u0bc1\u0ba4\u0bcd\u0ba4\u0bc1",
        refunds: "\u0baa\u0ba3\u0ba4\u0bcd\u0ba4\u0bc8\u0ba4\u0bcd \u0ba4\u0bbf\u0bb0\u0bc1\u0bae\u0bcd\u0baa\u0baa\u0bcd\u0baa\u0bc6\u0bb1\u0bc1\u0ba4\u0bb2\u0bcd",
        logout: "\u0bb5\u0bc6\u0bb3\u0bbf\u0baf\u0bc7\u0bb1\u0bc1"
    },
    kn: {
        billing_platform: "\u0cac\u0cbf\u0cb2\u0ccd\u0cb2\u0cbf\u0c82\u0c97\u0ccd \u0cb5\u0cc7\u0ca6\u0cbf\u0c95\u0cc6",
        admin_portal: "--- \u0c85\u0ca1\u0ccd\u0cae\u0cbf\u0ca8\u0ccd \u0caa\u0ccb\u0cb0\u0ccd\u0c9f\u0cb2\u0ccd ---",
        admin_metrics: "\u0c85\u0ca1\u0ccd\u0cae\u0cbf\u0ca8\u0ccd \u0cae\u0cc6\u0c9f\u0ccd\u0cb0\u0cbf\u0c95\u0ccd\u0cb8\u0ccd",
        failed_payments: "\u0cb5\u0cbf\u0cab\u0cb2\u0cb5\u0cbe\u0ca6 \u0caa\u0cbe\u0cb5\u0ca4\u0cbf\u0c97\u0cb3\u0cc1",
        audit_logs: "\u0c86\u0ca1\u0cbf\u0c9f\u0ccd \u0cb2\u0cbe\u0c97\u0ccd\u200c\u0c97\u0cb3\u0cc1",
        customer_portal: "--- \u0c97\u0ccd\u0cb0\u0cbe\u0cb9\u0c95 \u0caa\u0ccb\u0cb0\u0ccd\u0c9f\u0cb2\u0ccd ---",
        browse_plans: "\u0caa\u0ccd\u0cb2\u0cbe\u0ca8\u0ccd\u200c\u0c97\u0cb3\u0ca8\u0ccd\u0ca8\u0cc1 \u0cac\u0ccd\u0cb0\u0ccc\u0cb8\u0ccd \u0cae\u0cbe\u0ca1\u0cbf",
        my_invoices: "\u0ca8\u0ca8\u0ccd\u0ca8 \u0c87\u0ca8\u0ccd\u200c\u0cb5\u0cbe\u0caf\u0ccd\u0cb8\u0ccd\u200c\u0c97\u0cb3\u0cc1",
        change_plan: "\u0caa\u0ccd\u0cb2\u0cbe\u0ca8\u0ccd \u0cac\u0ca6\u0cb2\u0cbe\u0caf\u0cbf\u0cb8\u0cbf",
        pay_invoice: "\u0c87\u0ca8\u0ccd\u200c\u0cb5\u0cbe\u0caf\u0ccd\u0cb8\u0ccd \u0caa\u0cbe\u0cb5\u0ca4\u0cbf\u0cb8\u0cbf",
        refunds: "\u0cae\u0cb0\u0cc1\u0caa\u0cbe\u0cb5\u0ca4\u0cbf\u0c97\u0cb3\u0cc1",
        logout: "\u0cb2\u0cbe\u0c97\u0ccd \u0c94\u0c9f\u0ccd"
    }
};

function changeLanguage() {
    const lang = document.getElementById('langSelect').value;
    const dict = translations[lang];
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (dict && dict[key]) {
            element.textContent = dict[key];
        }
    });
}

function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active-section'));
    const section = document.getElementById(sectionId);
    if(section) section.classList.add('active-section');
    
    if (sectionId === 'metrics') loadMetrics();
    if (sectionId === 'plan_cards') loadPlans();
    if (sectionId === 'invoices') loadInvoices();
    if (sectionId === 'failed_payments') loadFailedPayments();
    if (sectionId === 'audit_logs') loadAuditLogs();
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "index.html";
}

// ================= CUSTOMER FEATURES =================
async function loadPlans() {
    try {
        const res = await fetch(`${BASE_URL}/plans`);
        if (res.ok) {
            const data = await res.json();
            const grid = document.getElementById('plansGrid');
            grid.innerHTML = '';
            data.forEach(plan => {
                let featuresHtml = '';
                try {
                    const features = JSON.parse(plan.features);
                    features.forEach(f => {
                        featuresHtml += `<li style="margin-bottom:8px; font-size:14px;">? ${f}</li>`;
                    });
                } catch(e) {
                    featuresHtml = `<li>${plan.features}</li>`;
                }
                
                grid.innerHTML += `
                    <div style="background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); padding: 25px; display: flex; flex-direction: column; transition: transform 0.3s; border-top: 5px solid #0056b3;">
                        <h3 style="margin-top:0; font-size: 22px; color: #333;">${plan.name}</h3>
                        <h1 style="font-size: 32px; color: #0056b3; margin: 10px 0;">Rs. ${plan.price}<span style="font-size:14px; color:#666; font-weight:normal;">/${plan.billing_interval}</span></h1>
                        <ul style="list-style: none; padding: 0; flex-grow: 1; margin: 20px 0; color: #555;">
                            ${featuresHtml}
                        </ul>
                        <button onclick="subscribeToPlan('${plan.id}')" style="background: #0056b3; color: white; border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; width: 100%; font-size: 16px;">Subscribe Now</button>
                    </div>
                `;
            });
        }
    } catch (e) { console.error("Error loading plans", e); }
}

function subscribeToPlan(planId) {
    showSection('upgrade');
    const select = document.getElementById('newPlanSelect');
    if(select) {
        let exists = false;
        for(let i=0; i<select.options.length; i++) {
            if(select.options[i].value === planId) exists = true;
        }
        if(!exists) {
            const opt = document.createElement('option');
            opt.value = planId;
            opt.text = planId;
            select.appendChild(opt);
        }
        select.value = planId;
    }
}

async function loadInvoices() {
    try {
        const response = await fetch(`${BASE_URL}/invoices`, { headers: { "Authorization": `Bearer ${token}` } });
        const invoices = await response.json();
        const tbody = document.getElementById('invoiceBody');
        tbody.innerHTML = '';
        invoices.forEach(inv => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${inv.id}</td>
                <td>${inv.subscription_id}</td>
                <td>${new Date(inv.created_at).toLocaleDateString()}</td>
                <td>Rs. ${inv.total_amount}</td>
                <td><strong>${inv.status.toUpperCase()}</strong></td>
                <td><button class="btn" style="background:#0033cc;" onclick="alert('PDF downloaded!')">?? PDF</button></td>
            `;
            tbody.appendChild(tr);
        });
    } catch(err) { console.error(err); }
}

async function upgradePlan() {
    const subId = document.getElementById('subIdInput').value;
    const newPlanId = document.getElementById('newPlanSelect').value;
    try {
        const response = await fetch(`${BASE_URL}/subscriptions/${subId}/upgrade`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', "Authorization": `Bearer ${token}` },
            body: JSON.stringify({ new_plan_id: newPlanId })
        });
        const result = await response.json();
        if (response.ok) {
            document.getElementById('prorationSummary').style.display = 'block';
            document.getElementById('summaryCredit').textContent = result.unused_credit.toFixed(2);
            document.getElementById('summaryCharge').textContent = result.new_plan_charge.toFixed(2);
            document.getElementById('summaryTotal').textContent = result.amount_due.toFixed(2);
            document.getElementById('upgradeError').textContent = '';
        } else {
            document.getElementById('upgradeError').textContent = result.detail;
            document.getElementById('prorationSummary').style.display = 'none';
        }
    } catch (e) { console.error(e); }
}

async function processPayment() {
    const invoiceId = document.getElementById('payInvoiceId').value;
    const amount = document.getElementById('payAmount').value;
    try {
        const response = await fetch(`${BASE_URL}/payments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', "Authorization": `Bearer ${token}` },
            body: JSON.stringify({ invoice_id: invoiceId, amount: parseFloat(amount), payment_method: "credit_card" })
        });
        const result = await response.json();
        document.getElementById('paymentResult').textContent = response.ok ? "Payment Successful!" : `Error: ${result.detail}`;
        document.getElementById('paymentResult').style.color = response.ok ? "green" : "red";
    } catch (e) { console.error(e); }
}

async function issueRefund() {
    const invoiceId = document.getElementById('refundInvoiceId').value;
    try {
        const response = await fetch(`${BASE_URL}/refunds`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', "Authorization": `Bearer ${token}` },
            body: JSON.stringify({ invoice_id: invoiceId, reason: "Customer requested cancellation" })
        });
        const result = await response.json();
        document.getElementById('refundResult').textContent = response.ok ? "Refund Issued Successfully!" : `Error: ${result.detail}`;
        document.getElementById('refundResult').style.color = response.ok ? "green" : "red";
    } catch (e) { console.error(e); }
}

// ================= ADMIN FEATURES =================
async function loadMetrics() {
    try {
        const sumRes = await fetch(`${BASE_URL}/dashboard/summary`, { headers: { "Authorization": `Bearer ${token}` } });
        if(sumRes.ok) {
            const summary = await sumRes.json();
            document.getElementById('mTotalCustomers').textContent = summary.total_customers;
            document.getElementById('mActiveSubs').textContent = summary.active_subscriptions;
            document.getElementById('mMRR').textContent = 'Rs. ' + summary.mrr.toFixed(2);
            document.getElementById('mChurn').textContent = summary.churn_rate.toFixed(1) + '%';
        }
        const revRes = await fetch(`${BASE_URL}/dashboard/revenue-by-plan`, { headers: { "Authorization": `Bearer ${token}` } });
        if(revRes.ok) {
            const revs = await revRes.json();
            const ul = document.getElementById('mRevenueList');
            ul.innerHTML = '';
            revs.forEach(r => {
                ul.innerHTML += `<li style="margin-bottom:10px; display:flex; justify-content:space-between;">
                    <strong>${r.plan}</strong> <span>Rs. ${r.revenue}</span>
                </li>`;
            });
        }
        const statRes = await fetch(`${BASE_URL}/dashboard/subscription-metrics`, { headers: { "Authorization": `Bearer ${token}` } });
        if(statRes.ok) {
            const stats = await statRes.json();
            const ul = document.getElementById('mStatusCounts');
            ul.innerHTML = '';
            for (const [status, count] of Object.entries(stats)) {
                ul.innerHTML += `<li style="margin-bottom:10px; display:flex; justify-content:space-between;">
                    <strong>${status.toUpperCase()}</strong> <span>${count}</span>
                </li>`;
            }
        }
    } catch(err) { console.error(err); }
}

async function loadFailedPayments() {
    try {
        const response = await fetch(`${BASE_URL}/payments/failed`, { headers: { "Authorization": `Bearer ${token}` } });
        if (response.ok) {
            const failed = await response.json();
            const tbody = document.getElementById('failedBody');
            tbody.innerHTML = '';
            failed.forEach(f => {
                tbody.innerHTML += `<tr>
                    <td>${f.invoice_id}</td>
                    <td>${f.customer_id}</td>
                    <td>Rs. ${f.amount}</td>
                    <td>${new Date(f.payment_date).toLocaleDateString()}</td>
                </tr>`;
            });
        }
    } catch (e) { console.error(e); }
}

async function loadAuditLogs() {
    try {
        const response = await fetch(`${BASE_URL}/audit-logs`, { headers: { "Authorization": `Bearer ${token}` } });
        if (response.ok) {
            const logs = await response.json();
            const tbody = document.getElementById('auditBody');
            tbody.innerHTML = '';
            logs.forEach(l => {
                tbody.innerHTML += `<tr>
                    <td>${new Date(l.created_at).toLocaleString()}</td>
                    <td><strong>${l.action.toUpperCase()}</strong></td>
                    <td>${l.entity_type}</td>
                    <td>${l.entity_id}</td>
                    <td>${l.performed_by}</td>
                </tr>`;
            });
        }
    } catch (e) { console.error(e); }
}

"""

with open("dashboard.js", "w", encoding="utf-8") as f:
    f.write(js_code)
