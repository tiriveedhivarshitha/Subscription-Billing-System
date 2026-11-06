
const BASE_URL = "http://127.0.0.1:8000";
const token = localStorage.getItem("token");

// ---- Auth Guard ----
if (!token) {
    window.location.href = "index.html";
} else {
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        if (payload.role !== "admin") {
            window.location.href = "index.html";
        }
    } catch (e) {
        window.location.href = "index.html";
    }
}

// =====================================================================
// POWER BI PAGE URLs
// Replace each URL below with the page-specific embed URL from Power BI.
// How to get them:
//   1. Go to app.powerbi.com → open your report
//   2. Click each tab (Overview, Plan Analytics, etc.)
//   3. Copy the full browser URL — it contains &pageName=ReportSectionXXXX
//   4. Use that URL in the embed format below
// =====================================================================
const DASHBOARD_PAGES = {
    'overview': {
        title: 'Overview',
        url: 'https://app.powerbi.com/reportEmbed?reportId=0b6f50a3-bb29-4da4-a3e7-f797c759c6c8&pageName=61a96283700070cc8bd0&autoAuth=true&ctid=4c49cc3b-7d9d-464e-8fc8-a10f91d8117a'
    },
    'plan-analytics': {
        title: 'Plan Analytics',
        url: 'https://app.powerbi.com/reportEmbed?reportId=0b6f50a3-bb29-4da4-a3e7-f797c759c6c8&pageName=b0d258830d7e3c21051b&autoAuth=true&ctid=4c49cc3b-7d9d-464e-8fc8-a10f91d8117a'
    },
    'cust-analytics': {
        title: 'Customer Analytics',
        url: 'https://app.powerbi.com/reportEmbed?reportId=0b6f50a3-bb29-4da4-a3e7-f797c759c6c8&pageName=e3184613332ed082716b&autoAuth=true&ctid=4c49cc3b-7d9d-464e-8fc8-a10f91d8117a'
    },
    'payments-dash': {
        title: 'Payments Overview',
        url: 'https://app.powerbi.com/reportEmbed?reportId=0b6f50a3-bb29-4da4-a3e7-f797c759c6c8&pageName=e5404f6101edc30593e2&autoAuth=true&ctid=4c49cc3b-7d9d-464e-8fc8-a10f91d8117a'
    }
};

// ---- Dashboard group toggle (expand/collapse sub-items) ----
function toggleDashboardGroup() {
    const grp = document.getElementById('grp-dashboard');
    const sub = document.getElementById('sub-dashboard');
    grp.classList.toggle('open');
    sub.classList.toggle('open');
}

// ---- Switch Power BI page inside the dashboard iframe ----
function showDashPage(pageKey, title, clickedEl) {
    // Show dashboard section
    showSection('dashboard');

    // Clear all sub-item highlights, highlight clicked
    document.querySelectorAll('.nav-sub-item').forEach(el => el.classList.remove('active-nav'));
    if (clickedEl) clickedEl.classList.add('active-nav');

    // Update title bar
    document.getElementById('dashPageTitle').textContent = title;

    // Swap iframe src
    const page = DASHBOARD_PAGES[pageKey];
    if (page) {
        const frame = document.getElementById('biFrame');
        // Only reload if URL actually changed (avoids flicker)
        if (frame.src !== page.url) {
            frame.src = page.url;
        }
    }
}

// ---- Section Navigation (non-dashboard sections) ----
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active-section'));
    const section = document.getElementById(sectionId);
    if (section) section.classList.add('active-section');

    // Clear all top-level nav highlights
    document.querySelectorAll('.nav-item').forEach(a => a.classList.remove('active-nav'));

    if (sectionId !== 'dashboard') {
        // Highlight the matching top-level nav item
        const navEl = document.getElementById('nav-' + sectionId);
        if (navEl) navEl.classList.add('active-nav');
        // Clear sub-item highlights when leaving dashboard
        document.querySelectorAll('.nav-sub-item').forEach(el => el.classList.remove('active-nav'));
    }

    // Load data
    if (sectionId === 'plans')            loadPlans();
    if (sectionId === 'archived_plans')   loadArchivedPlans();
    if (sectionId === 'failed_payments')  loadFailedPayments();
    if (sectionId === 'audit_logs')       loadAuditLogs();
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "index.html";
}

// ===================== FEATURE EXTRACTOR =====================
function extractFeatures(featuresData) {
    if (!featuresData) return [];
    if (Array.isArray(featuresData)) return featuresData;
    if (typeof featuresData === 'object') {
        if (Array.isArray(featuresData.features)) return featuresData.features;
        const all = [];
        for (const [key, val] of Object.entries(featuresData)) {
            if (Array.isArray(val)) {
                val.forEach(v => all.push(`${key}: ${v}`));
            } else if (typeof val === 'string') {
                all.push(`${key}: ${val}`);
            }
        }
        return all;
    }
    return [];
}

// ===================== PLANS =====================
function toggleAddPlanForm() {
    const form = document.getElementById('addPlanForm');
    form.style.display = (form.style.display === 'block') ? 'none' : 'block';
    document.getElementById('planFormMsg').textContent = '';
}

async function loadPlans() {
    try {
        const res   = await fetch(`${BASE_URL}/admin/plans`, { headers: { "Authorization": `Bearer ${token}` } });
        if (!res.ok) return;
        const plans = await res.json();
        const grid  = document.getElementById('plansGrid');
        grid.innerHTML = '';

        if (plans.length === 0) {
            grid.innerHTML = '<div class="empty-state">No active plans found.</div>';
            return;
        }

        plans.forEach(plan => {
            let featuresHtml = '';
            try {
                const features = extractFeatures(plan.features);
                featuresHtml = features.length > 0
                    ? features.map(f => `<li>${f}</li>`).join('')
                    : '<li style="color:#aaa;">No features listed</li>';
            } catch (e) { featuresHtml = `<li>${plan.features}</li>`; }

            grid.innerHTML += `
                <div class="plan-card">
                    <h3>${plan.name}</h3>
                    <div class="price">Rs. ${plan.price}<span>/${plan.billing_interval}</span></div>
                    <div class="meta">Trial: ${plan.trial_days} days &nbsp;|&nbsp; ID: ${plan.id}</div>
                    <ul>${featuresHtml}</ul>
                    <div class="card-actions">
                        <button class="btn-edit"
                            onclick="openEditModal('${plan.id}','${plan.name}','${plan.billing_interval}',${plan.trial_days},'active')">
                            Edit
                        </button>
                        <button class="btn-archive" onclick="archivePlan('${plan.id}','${plan.name}')">Archive</button>
                    </div>
                </div>`;
        });
    } catch (e) { console.error("loadPlans error:", e); }
}

async function archivePlan(planId, planName) {
    if (!confirm(`Archive plan "${planName}"? It will move to Archived Plans.`)) return;
    try {
        const res = await fetch(`${BASE_URL}/admin/plans/archieve/${planId}`, {
            method: 'PUT', headers: { "Authorization": `Bearer ${token}` }
        });
        const result = await res.json();
        if (res.ok) { alert(`"${planName}" archived.`); loadPlans(); }
        else alert('Error: ' + (result.detail || 'Could not archive.'));
    } catch (e) { console.error(e); }
}

async function submitNewPlan() {
    const name        = document.getElementById('newPlanName').value.trim();
    const price       = parseFloat(document.getElementById('newPlanPrice').value);
    const interval    = document.getElementById('newPlanInterval').value;
    const trial       = parseInt(document.getElementById('newPlanTrial').value) || 0;
    const status      = document.getElementById('newPlanStatus').value;
    const rawFeatures = document.getElementById('newPlanFeatures').value.trim();
    const msgEl       = document.getElementById('planFormMsg');

    if (!name || isNaN(price) || !rawFeatures) {
        msgEl.style.color = '#dc3545';
        msgEl.textContent = 'Please fill in Name, Price, and at least one Feature.';
        return;
    }

    const featureList = rawFeatures.split('\n').map(f => f.trim()).filter(f => f.length > 0);
    const body = { name, price, billing_interval: interval, trial_days: trial, features: { features: featureList }, status };

    try {
        const res    = await fetch(`${BASE_URL}/admin/plans`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(body)
        });
        const result = await res.json();
        if (res.ok) {
            msgEl.style.color = '#28a745';
            msgEl.textContent = 'Plan added successfully!';
            document.getElementById('newPlanName').value     = '';
            document.getElementById('newPlanPrice').value    = '';
            document.getElementById('newPlanTrial').value    = '0';
            document.getElementById('newPlanFeatures').value = '';
            setTimeout(() => { toggleAddPlanForm(); loadPlans(); }, 1200);
        } else {
            msgEl.style.color = '#dc3545';
            msgEl.textContent = 'Error: ' + (result.detail || JSON.stringify(result));
        }
    } catch (e) { msgEl.style.color='#dc3545'; msgEl.textContent='Server error.'; console.error(e); }
}

// ===================== EDIT PLAN MODAL =====================
function openEditModal(planId, planName, billingInterval, trialDays, status) {
    document.getElementById('editPlanId').value       = planId;
    document.getElementById('editPlanName').value     = planName;
    document.getElementById('editPlanInterval').value = billingInterval;
    document.getElementById('editPlanTrial').value    = trialDays;
    document.getElementById('editPlanStatus').value   = status;
    document.getElementById('editPlanMsg').textContent = '';
    document.getElementById('editPlanModal').classList.add('open');
}

function closeEditModal() {
    document.getElementById('editPlanModal').classList.remove('open');
}

async function submitEditPlan() {
    const planId   = document.getElementById('editPlanId').value;
    const name     = document.getElementById('editPlanName').value.trim();
    const interval = document.getElementById('editPlanInterval').value;
    const trial    = parseInt(document.getElementById('editPlanTrial').value) || 0;
    const status   = document.getElementById('editPlanStatus').value;
    const msgEl    = document.getElementById('editPlanMsg');

    if (!name) { msgEl.style.color='#dc3545'; msgEl.textContent='Plan name cannot be empty.'; return; }

    try {
        const res = await fetch(`${BASE_URL}/admin/plan/${planId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ name, billing_interval: interval, trial_days: trial, status })
        });
        const result = await res.json();
        if (res.ok) {
            msgEl.style.color = '#28a745';
            msgEl.textContent = 'Plan updated successfully!';
            setTimeout(() => { closeEditModal(); loadPlans(); }, 1000);
        } else {
            msgEl.style.color = '#dc3545';
            msgEl.textContent = 'Error: ' + (result.detail || 'Could not update plan.');
        }
    } catch (e) { msgEl.style.color='#dc3545'; msgEl.textContent='Server error.'; console.error(e); }
}

// ===================== ARCHIVED PLANS =====================
async function loadArchivedPlans() {
    try {
        const res   = await fetch(`${BASE_URL}/admin/plans/archived`, { headers: { "Authorization": `Bearer ${token}` } });
        if (!res.ok) return;
        const plans = await res.json();
        const grid  = document.getElementById('archivedPlansGrid');
        grid.innerHTML = '';

        if (plans.length === 0) {
            grid.innerHTML = '<div class="empty-state">No archived plans found.</div>';
            return;
        }

        plans.forEach(plan => {
            let featuresHtml = '';
            try {
                const features = extractFeatures(plan.features);
                featuresHtml = features.length > 0
                    ? features.map(f => `<li>${f}</li>`).join('')
                    : '<li style="color:#aaa;">No features listed</li>';
            } catch (e) { featuresHtml = `<li>${plan.features}</li>`; }

            grid.innerHTML += `
                <div class="plan-card" style="border-top-color:#ffc107;">
                    <span class="archived-badge">ARCHIVED</span>
                    <h3>${plan.name}</h3>
                    <div class="price">Rs. ${plan.price}<span>/${plan.billing_interval}</span></div>
                    <div class="meta">Trial: ${plan.trial_days} days &nbsp;|&nbsp; ID: ${plan.id}</div>
                    <ul>${featuresHtml}</ul>
                    <button class="btn-activate" onclick="activatePlan('${plan.id}','${plan.name}')">Activate Plan</button>
                </div>`;
        });
    } catch (e) { console.error("loadArchivedPlans error:", e); }
}

async function activatePlan(planId, planName) {
    if (!confirm(`Activate plan "${planName}"? It will be restored to active status.`)) return;
    try {
        const res = await fetch(`${BASE_URL}/admin/plan/${planId}`, {
            method: 'PUT', headers: { "Authorization": `Bearer ${token}` }
        });
        const result = await res.json();
        if (res.ok) { alert(`"${planName}" activated.`); loadArchivedPlans(); }
        else alert('Error: ' + (result.detail || 'Could not activate.'));
    } catch (e) { console.error(e); }
}

// ===================== FAILED PAYMENTS =====================
async function loadFailedPayments() {
    try {
        const res  = await fetch(`${BASE_URL}/admin/payments/failed`, { headers: { "Authorization": `Bearer ${token}` } });
        const tbody = document.getElementById('failedPaymentsBody');
        if (!res.ok) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#888;">Could not load failed payments.</td></tr>';
            return;
        }
        const data = await res.json();
        tbody.innerHTML = '';
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#28a745;font-weight:bold;">No failed payments. All good!</td></tr>';
            return;
        }
        data.forEach(p => {
            tbody.innerHTML += `<tr>
                <td>${p.invoice_id}</td>
                <td>${p.payment_reference || '—'}</td>
                <td>Rs. ${p.amount}</td>
                <td>${p.payment_method || '—'}</td>
                <td>${p.payment_date ? new Date(p.payment_date).toLocaleDateString() : '—'}</td>
                <td><span class="badge-failed">FAILED</span></td>
            </tr>`;
        });
    } catch (e) { console.error("loadFailedPayments error:", e); }
}

// ===================== AUDIT LOGS =====================
async function loadAuditLogs() {
    try {
        const response = await fetch(`${BASE_URL}/admin/audit-logs`, { headers: { "Authorization": `Bearer ${token}` } });
        if (response.ok) {
            const logs  = await response.json();
            const tbody = document.getElementById('auditBody');
            tbody.innerHTML = '';
            if (logs.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#888;">No audit logs found.</td></tr>';
                return;
            }
            logs.forEach(l => {
                tbody.innerHTML += `<tr>
                    <td>${new Date(l.date).toLocaleString()}</td>
                    <td><strong>${l.action.toUpperCase()}</strong></td>
                    <td>${l.entity_type}</td>
                    <td>${l.entity_id}</td>
                    <td>${l.user}</td>
                </tr>`;
            });
        }
    } catch (e) { console.error("loadAuditLogs error:", e); }
}

// ---- Auto-load: show dashboard → Overview on page load ----
window.addEventListener('DOMContentLoaded', () => {
    showDashPage('overview', 'Overview', document.getElementById('nav-overview'));
});
