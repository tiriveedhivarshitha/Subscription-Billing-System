// ============================================================
//  Customer Dashboard JS
// ============================================================

const BASE = "http://127.0.0.1:8000";

// ---- Auth guard ----
const token = localStorage.getItem("token");
const role  = localStorage.getItem("role");
if (!token || role !== "user") {
  window.location.href = "index.html";
}
const AUTH = { Authorization: "Bearer " + token, "Content-Type": "application/json" };

// ---- Decode JWT payload ----
function decodeJWT(t) {
  try { return JSON.parse(atob(t.split('.')[1])); }
  catch(e) { return {}; }
}
const jwtPayload = decodeJWT(token);

// ---- State ----
let currentPlanId        = null;
let currentPlanName      = null;
let currentPrice         = null;
let subscribedPlanIds    = new Set(); // plan_ids with active/trial subscription
let renewingNotifCardId  = null;      // DOM id of notification card being renewed

// ==============================================================
//  NAVIGATION
// ==============================================================
const SECTION_KEYS = ['plans','invoices','subscriptions','notifications','profile'];

function showSection(name) {
  SECTION_KEYS.forEach(k => {
    const el = document.getElementById("section-" + k);
    if (el) el.style.display = "none";
  });
  const target = document.getElementById("section-" + name);
  if (target) target.style.display = "block";

  document.querySelectorAll(".nav-item").forEach(el => el.classList.remove("active"));
  const idx = SECTION_KEYS.indexOf(name);
  const navItems = document.querySelectorAll(".nav-item");
  if (navItems[idx]) navItems[idx].classList.add("active");

  if (name === "plans")         loadPlans();
  if (name === "invoices")      loadInvoices();
  if (name === "subscriptions") loadSubscriptions();
  if (name === "notifications") loadNotifications();
  if (name === "profile")       loadProfile();
}

// ==============================================================
//  TOAST
// ==============================================================
function showToast(msg, type = "") {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.className = "toast show" + (type ? " toast-" + type : "");
  setTimeout(() => { t.className = "toast"; }, 3500);
}

// ==============================================================
//  FEATURES EXTRACTOR
// ==============================================================
function extractFeatures(fd) {
  if (!fd) return [];
  const list = [];
  if (Array.isArray(fd)) {
    fd.forEach(item => {
      if (typeof item === "string") list.push(item);
      else if (typeof item === "object") {
        Object.entries(item).forEach(([k,v]) => {
          if (Array.isArray(v)) v.forEach(val => list.push(val));
          else list.push(`${k}: ${v}`);
        });
      }
    });
    return list;
  }
  if (typeof fd === "object") {
    Object.entries(fd).forEach(([k,v]) => {
      if (k === "features" && Array.isArray(v)) { v.forEach(f => list.push(f)); return; }
      if (Array.isArray(v)) v.forEach(val => list.push(val));
      else list.push(`${k}: ${v}`);
    });
    return list;
  }
  return [];
}

// ==============================================================
//  FETCH SUBSCRIBED PLAN IDs (active + trial)
// ==============================================================
async function fetchSubscribedPlanIds() {
  try {
    const res = await fetch(`${BASE}/customer/my-active-subscriptions`, { headers: AUTH });
    if (!res.ok) return;
    const data = await res.json();
    subscribedPlanIds = new Set(data.map(s => s.plan_id));
  } catch (e) { /* silent */ }
}

// ==============================================================
//  PLANS
// ==============================================================
let searchTimer = null;

function onPlanSearch(val) {
  clearTimeout(searchTimer);
  if (!val.trim()) { loadPlans(); return; }
  searchTimer = setTimeout(() => searchPlanByName(val.trim()), 400);
}

async function loadPlans() {
  document.getElementById("plan-search").value = "";
  document.getElementById("plans-container").innerHTML = '<div class="loading">Loading plans...</div>';
  try {
    await fetchSubscribedPlanIds();
    const res = await fetch(`${BASE}/customer/plans`);
    if (!res.ok) throw new Error("Failed to load plans");
    const data = await res.json();
    renderPlanCards(data);
  } catch (e) {
    document.getElementById("plans-container").innerHTML =
      `<div class="empty-state"><div class="icon">⚠️</div><p>${e.message}</p></div>`;
  }
}

async function searchPlanByName(name) {
  document.getElementById("plans-container").innerHTML = '<div class="loading">Searching...</div>';
  try {
    const res = await fetch(`${BASE}/customer/plans/${encodeURIComponent(name)}`);
    if (!res.ok) { renderPlanCards([]); return; }
    const data = await res.json();
    renderPlanCards(data);
  } catch(e) { renderPlanCards([]); }
}

function renderPlanCards(plans) {
  const container = document.getElementById("plans-container");
  if (!plans || plans.length === 0) {
    container.innerHTML = `<div class="empty-state"><div class="icon">📭</div><p>No plans found</p></div>`;
    return;
  }
  const colors = ["#7c83fd","#27ae60","#e74c3c","#f39c12","#2980b9","#8e44ad"];
  container.innerHTML = plans.map((plan, i) => {
    const features    = extractFeatures(plan.features);
    const color       = colors[i % colors.length];
    const total       = (plan.price * 1.18).toFixed(2);
    const isSubscribed = subscribedPlanIds.has(plan.plan_id);
    const hasTrial    = plan.trial_days > 0 && !isSubscribed;
    const featureHTML = features.length
      ? features.map(f => `<li>${f}</li>`).join("")
      : `<li>Standard features included</li>`;

    return `
      <div class="plan-card" style="border-top-color:${color};">
        <div class="plan-card-body">
          <div class="plan-name">${escHtml(plan.name)}</div>
          <div class="plan-price">&#8377;${Number(plan.price).toLocaleString('en-IN')}
            <span>/ ${escHtml(plan.billing_interval || "month")}</span>
          </div>
          <div class="plan-gst-note">+18% GST &nbsp;|&nbsp; Total: <strong>&#8377;${Number(total).toLocaleString('en-IN')}</strong></div>
          <div class="features-label">What's included</div>
          <ul class="features-list">${featureHTML}</ul>
        </div>
        <div class="plan-card-footer">
          ${isSubscribed
            ? `<span class="trial-active-badge">&#10003; Subscribed</span>`
            : `<button class="btn btn-primary" onclick="openPayModal('${plan.plan_id}','${escStr(plan.name)}',${plan.price})">Subscribe Now</button>`
          }
          ${hasTrial
            ? `<button class="btn btn-secondary" onclick="takeFreeTrial('${plan.plan_id}','${escStr(plan.name)}',this)">
                 Free Trial (${plan.trial_days} days)
               </button>`
            : ""
          }
        </div>
      </div>`;
  }).join("");
}

function escStr(s) { return String(s).replace(/\\/g,"\\\\").replace(/'/g,"\\'"); }
function escHtml(s) {
  return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

// ==============================================================
//  PAYMENT MODAL
// ==============================================================
function openPayModal(planId, planName, price) {
  currentPlanId   = planId;
  currentPlanName = planName;
  currentPrice    = price;

  const tax   = (price * 0.18).toFixed(2);
  const total = (price * 1.18).toFixed(2);

  document.getElementById("modal-plan-name").textContent  = "Subscribe: " + planName;
  document.getElementById("modal-plan-label").textContent = planName;
  document.getElementById("modal-subtotal").textContent   = "₹" + Number(price).toLocaleString('en-IN');
  document.getElementById("modal-tax").textContent        = "₹" + Number(tax).toLocaleString('en-IN');
  document.getElementById("modal-total").textContent      = "₹" + Number(total).toLocaleString('en-IN');

  document.getElementById("payment-result").className     = "payment-result hidden";
  document.getElementById("payment-form-wrap").style.display = "block";
  document.getElementById("modal-footer").innerHTML = `
    <button class="btn btn-secondary" onclick="closePayModal()">Cancel</button>
    <button class="btn btn-primary" id="confirm-pay-btn" onclick="confirmPayment()">Confirm &amp; Pay</button>`;

  document.getElementById("pay-modal-overlay").classList.add("open");
}

function closePayModal() {
  document.getElementById("pay-modal-overlay").classList.remove("open");
  currentPlanId = currentPlanName = currentPrice = renewingNotifCardId = null;
}

async function confirmPayment() {
  if (!currentPlanId) return;
  const method = document.getElementById("payment-method").value;
  const btn    = document.getElementById("confirm-pay-btn");
  btn.disabled = true;
  btn.textContent = "Processing...";

  try {
    const res  = await fetch(`${BASE}/customer/payments/process`, {
      method: "POST", headers: AUTH,
      body: JSON.stringify({ plan_id: currentPlanId, payment_method: method })
    });
    const data = await res.json();

    document.getElementById("payment-form-wrap").style.display = "none";
    document.getElementById("modal-footer").innerHTML =
      `<button class="btn btn-secondary" onclick="closePayModal()">Close</button>`;

    const resultDiv = document.getElementById("payment-result");
    if (data.status === "success") {
      subscribedPlanIds.add(currentPlanId);

      // If this was a renewal from notifications, remove that card
      if (renewingNotifCardId) {
        const card = document.getElementById(renewingNotifCardId);
        if (card) {
          card.style.transition = "opacity 0.4s, transform 0.4s";
          card.style.opacity    = "0";
          card.style.transform  = "translateX(40px)";
          setTimeout(() => {
            card.remove();
            // If no cards left, show "All Good" message
            const list = document.getElementById("notifications-container");
            if (list && list.querySelectorAll(".notif-card").length === 0) {
              list.innerHTML = `
                <div class="notif-empty">
                  <div class="icon">✅</div>
                  <h3>All Good!</h3>
                  <p>No subscriptions are expiring within the next 7 days.</p>
                </div>`;
              // Hide sidebar badge
              const badge = document.getElementById("notif-count-badge");
              badge.style.display = "none";
            } else {
              // Update badge count
              const badge = document.getElementById("notif-count-badge");
              const remaining = list.querySelectorAll(".notif-card").length;
              badge.textContent = remaining;
              if (remaining === 0) badge.style.display = "none";
            }
          }, 450);
        }
        renewingNotifCardId = null;
      }

      resultDiv.className = "payment-result success";
      resultDiv.innerHTML = `
        ✅ Payment Successful! Subscription Renewed.<br>
        <small style="font-weight:400">Transaction ID: <strong>${data.transaction_id}</strong></small><br><br>
        <button class="btn btn-primary" onclick="closePayModal(); showSection('invoices')" style="margin-top:4px;">
          View My Invoices
        </button>`;
      showToast("Payment successful! 🎉", "success");
    } else {
      resultDiv.className = "payment-result failed";
      resultDiv.innerHTML = `
        ❌ Payment Failed<br>
        <small style="font-weight:400">${data.reason || "Please try again later."}</small><br>
        <small>Transaction ID: ${data.transaction_id}</small>`;
      showToast("Payment failed. Try again.", "error");
    }
    resultDiv.classList.remove("hidden");
  } catch(e) {
    showToast("Network error. Please try again.", "error");
    btn.disabled = false;
    btn.textContent = "Confirm & Pay";
  }
}

// ==============================================================
//  FREE TRIAL
// ==============================================================
async function takeFreeTrial(planId, planName, btnEl) {
  if (!confirm(`Start a free trial for "${planName}"?`)) return;
  btnEl.disabled = true;
  btnEl.textContent = "Starting...";
  try {
    const res  = await fetch(`${BASE}/customer/subscriptions/trial`, {
      method: "POST", headers: AUTH,
      body: JSON.stringify({ plan_id: planId, payment_method: "UPI" })
    });
    const data = await res.json();
    if (res.ok && data.status === "trial_started") {
      subscribedPlanIds.add(planId);
      showToast(`Free trial started for "${planName}" 🎉`, "success");
      btnEl.replaceWith(Object.assign(document.createElement("span"), {
        className: "trial-active-badge", textContent: "✓ Trial Active"
      }));
    } else {
      throw new Error(data.detail || "Could not start trial");
    }
  } catch(e) {
    showToast("Error: " + e.message, "error");
    btnEl.disabled = false;
    btnEl.textContent = "Free Trial";
  }
}

// ==============================================================
//  INVOICES
// ==============================================================
async function loadInvoices() {
  document.getElementById("invoice-filter").value = "";
  renderInvoicesTable(null, true);
  try {
    const res = await fetch(`${BASE}/customer/invoices`, { headers: AUTH });
    if (res.status === 404) { renderInvoicesTable([]); return; }
    if (!res.ok) throw new Error("Failed to load invoices");
    renderInvoicesTable(await res.json());
  } catch(e) { renderInvoicesTable(null, false, e.message); }
}

async function searchInvoiceById() {
  const id = document.getElementById("invoice-filter").value.trim();
  if (!id) { showToast("Enter an Invoice ID first"); return; }
  renderInvoicesTable(null, true);
  try {
    const res = await fetch(`${BASE}/customer/invoices/${encodeURIComponent(id)}`, { headers: AUTH });
    if (!res.ok) { renderInvoicesTable([]); return; }
    const data = await res.json();
    renderInvoicesTable(Array.isArray(data) ? data : [data]);
  } catch(e) { renderInvoicesTable(null, false, e.message); }
}

function renderInvoicesTable(data, loading = false, error = null) {
  const tbody = document.getElementById("invoices-tbody");
  if (loading) { tbody.innerHTML = `<tr><td colspan="8" class="loading">Loading...</td></tr>`; return; }
  if (error)   { tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:40px;color:#888;">⚠️ ${error}</td></tr>`; return; }
  if (!data || data.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:40px;color:#888;">No invoices found</td></tr>`;
    return;
  }
  tbody.innerHTML = data.map(inv => {
    const date = inv.invoice_date ? new Date(inv.invoice_date).toLocaleDateString("en-IN") : "-";
    return `
      <tr>
        <td>${inv.invoice_id}</td>
        <td>${inv.subscription_no || "-"}</td>
        <td>${date}</td>
        <td>&#8377;${Number(inv.sub_total).toLocaleString('en-IN')}</td>
        <td>&#8377;${Number(inv.tax_amount).toLocaleString('en-IN')}</td>
        <td>&#8377;${Number(inv.total_amount).toLocaleString('en-IN')}</td>
        <td><span class="badge ${inv.status==='paid'?'badge-paid':'badge-pending'}">${inv.status}</span></td>
        <td>
          <button class="btn btn-primary" style="padding:7px 14px;font-size:12px;"
            onclick="downloadInvoice('${inv.invoice_id}')">&#8595; PDF</button>
        </td>
      </tr>`;
  }).join("");
}

function downloadInvoice(id) {
  window.open(`${BASE}/customer/invoices/${id}/pdf`, "_blank");
}

// ==============================================================
//  MY SUBSCRIPTIONS
// ==============================================================
async function loadSubscriptions() {
  document.getElementById("subscriptions-container").innerHTML = '<div class="loading">Loading...</div>';
  try {
    const res = await fetch(`${BASE}/customer/my-active-subscriptions`, { headers: AUTH });
    if (!res.ok) throw new Error("Failed to load subscriptions");
    renderSubscriptions(await res.json());
  } catch(e) {
    document.getElementById("subscriptions-container").innerHTML =
      `<div class="empty-state"><div class="icon">⚠️</div><p>${e.message}</p></div>`;
  }
}

function renderSubscriptions(subs) {
  const c = document.getElementById("subscriptions-container");
  if (!subs || subs.length === 0) {
    c.innerHTML = `<div class="empty-state"><div class="icon">📋</div>
      <p>No active subscriptions yet. <a href="#" onclick="showSection('plans')">Explore Plans →</a></p></div>`;
    return;
  }
  c.innerHTML = subs.map(sub => {
    const endDate  = sub.end_date ? new Date(sub.end_date).toLocaleDateString("en-IN") : "-";
    const daysLeft = sub.end_date ? Math.ceil((new Date(sub.end_date) - new Date()) / 86400000) : null;
    const label    = sub.status === "trial" ? "Trial" : "Active";
    const expiring = daysLeft !== null && daysLeft <= 7;
    return `
      <div class="sub-card" style="border-left-color:${expiring ? '#e74c3c' : '#27ae60'}">
        <h4>${sub.subscription_id}</h4>
        <div class="sub-info">Plan ID: <span>${sub.plan_id}</span></div>
        <div class="sub-info">Expires: <span>${endDate}</span></div>
        ${daysLeft !== null ? `<div class="sub-info">Days Left: <span style="color:${daysLeft<=3?'#e74c3c':daysLeft<=7?'#f39c12':'#27ae60'}">${daysLeft} day${daysLeft!==1?'s':''}</span></div>` : ""}
        <div style="margin-top:10px;">
          <span class="badge badge-active">${label}</span>
          ${expiring ? `<span class="badge" style="background:#fdecea;color:#c0392b;margin-left:6px;">Expiring Soon</span>` : ""}
        </div>
      </div>`;
  }).join("");
}

// ==============================================================
//  NOTIFICATIONS — subscriptions ending within 7 days
// ==============================================================
async function loadNotifications() {
  document.getElementById("notifications-container").innerHTML =
    '<div class="loading">Checking your subscriptions...</div>';
  try {
    // Fetch subscriptions AND plans in parallel
    const [subRes, planRes] = await Promise.all([
      fetch(`${BASE}/customer/my-active-subscriptions`, { headers: AUTH }),
      fetch(`${BASE}/customer/plans`)
    ]);

    if (!subRes.ok) throw new Error("Could not fetch subscriptions");
    const subs  = await subRes.json();

    // Build planId → {name, price} map
    let planMap = {};
    if (planRes.ok) {
      const plans = await planRes.json();
      plans.forEach(p => { planMap[p.plan_id] = { name: p.name, price: p.price }; });
    }

    const now = new Date();
    const expiring = subs
      .map(s => {
        const end    = new Date(s.end_date);
        const days   = Math.ceil((end - now) / 86400000);
        const planInfo = planMap[s.plan_id] || { name: s.plan_id, price: null };
        return { ...s, daysLeft: days, endDate: end, planName: planInfo.name, planPrice: planInfo.price };
      })
      .filter(s => s.daysLeft <= 7)
      .sort((a, b) => a.daysLeft - b.daysLeft);

    // Update sidebar badge
    const badge = document.getElementById("notif-count-badge");
    if (expiring.length > 0) {
      badge.textContent    = expiring.length;
      badge.style.display  = "inline-flex";
    } else {
      badge.style.display  = "none";
    }

    renderNotifications(expiring);
  } catch(e) {
    document.getElementById("notifications-container").innerHTML =
      `<div class="empty-state"><div class="icon">⚠️</div><p>${e.message}</p></div>`;
  }
}

function renderNotifications(expiring) {
  const c = document.getElementById("notifications-container");
  if (expiring.length === 0) {
    c.innerHTML = `
      <div class="notif-empty">
        <div class="icon">✅</div>
        <h3>All Good!</h3>
        <p>No subscriptions are expiring within the next 7 days.</p>
      </div>`;
    return;
  }

  c.innerHTML = expiring.map((sub, idx) => {
    const days      = sub.daysLeft;
    const isUrgent  = days <= 2;
    const isSafe    = days >= 5;
    const cardClass = isUrgent ? "urgent" : isSafe ? "safe" : "";
    const icon      = days <= 0 ? "🔴" : days <= 2 ? "🚨" : days <= 4 ? "⚠️" : "🕐";
    const dateStr   = sub.endDate.toLocaleDateString("en-IN", { day:"numeric", month:"long", year:"numeric" });
    const statusLabel = sub.status === "trial" ? "Free Trial" : "Subscription";
    const cardId    = `notif-card-${idx}`;

    let message = "";
    if (days <= 0)       message = `Your <strong>${statusLabel}</strong> for <strong>${escHtml(sub.planName)}</strong> has already expired!`;
    else if (days === 1) message = `Your <strong>${statusLabel}</strong> for <strong>${escHtml(sub.planName)}</strong> expires <strong>tomorrow</strong> (${dateStr}).`;
    else                 message = `Your <strong>${statusLabel}</strong> for <strong>${escHtml(sub.planName)}</strong> expires in <strong>${days} days</strong> on ${dateStr}.`;

    // Renew button — only show if we have plan price
    const renewBtn = sub.planPrice !== null
      ? `<button class="btn btn-warning" style="margin-top:12px;padding:9px 18px;font-size:13px;"
           onclick="renewFromNotification('${sub.plan_id}','${escStr(sub.planName)}',${sub.planPrice},'${cardId}')">
           🔄 Renew Now
         </button>`
      : `<button class="btn btn-warning" style="margin-top:12px;padding:9px 18px;font-size:13px;"
           onclick="showSection('plans')">
           Go to Plans
         </button>`;

    return `
      <div class="notif-card ${cardClass}" id="${cardId}">
        <div class="notif-icon">${icon}</div>
        <div class="notif-body">
          <div class="notif-title">${statusLabel} Expiring — ${escHtml(sub.planName)}</div>
          <div class="notif-detail">${message}</div>
          <div class="notif-detail" style="margin-top:4px;color:#aaa;font-size:12px;">
            Subscription ID: ${sub.subscription_id}
          </div>
          ${renewBtn}
        </div>
        <div class="notif-days ${isSafe ? 'safe-days' : ''}">
          <div class="days-num">${days <= 0 ? '0' : days}</div>
          <div class="days-label">${days <= 0 ? 'expired' : 'days left'}</div>
        </div>
      </div>`;
  }).join("");
}

// ==============================================================
//  RENEW FROM NOTIFICATION
// ==============================================================
function renewFromNotification(planId, planName, price, cardId) {
  renewingNotifCardId = cardId;  // remember which card to remove after success
  openPayModal(planId, planName, price);
  // Update modal title to say "Renew" instead of "Subscribe"
  document.getElementById("modal-plan-name").textContent = "Renew: " + planName;
}

// ==============================================================
//  PROFILE
// ==============================================================
async function loadProfile() {
  // Populate from JWT
  const email      = jwtPayload.mail       || "N/A";
  const customerId = jwtPayload.customer_id || "N/A";

  // Avatar initial from email
  const initial = email.charAt(0).toUpperCase();
  document.getElementById("profile-avatar").textContent       = initial;
  document.getElementById("profile-display-name").textContent = email.split("@")[0];
  document.getElementById("profile-customer-id").textContent  = customerId;
  document.getElementById("profile-email").textContent        = email;

  // Member since — decoded from JWT iat if present, else today
  if (jwtPayload.iat) {
    const since = new Date(jwtPayload.iat * 1000).toLocaleDateString("en-IN", { day:"numeric", month:"long", year:"numeric" });
    document.getElementById("profile-since").textContent = since;
  } else {
    document.getElementById("profile-since").textContent = "N/A";
  }

  // Load stats in parallel
  document.getElementById("stat-active").textContent   = "...";
  document.getElementById("stat-invoices").textContent = "...";
  document.getElementById("stat-spent").textContent    = "...";

  try {
    const [subRes, invRes] = await Promise.all([
      fetch(`${BASE}/customer/my-active-subscriptions`, { headers: AUTH }),
      fetch(`${BASE}/customer/invoices`, { headers: AUTH })
    ]);

    // Active plans count
    if (subRes.ok) {
      const subs = await subRes.json();
      document.getElementById("stat-active").textContent = subs.length;
    } else {
      document.getElementById("stat-active").textContent = "0";
    }

    // Invoice count + total spent
    if (invRes.ok) {
      const invs = await invRes.json();
      document.getElementById("stat-invoices").textContent = invs.length;
      const spent = invs.reduce((sum, inv) => sum + (Number(inv.total_amount) || 0), 0);
      document.getElementById("stat-spent").textContent = Number(spent.toFixed(0)).toLocaleString('en-IN');
    } else {
      document.getElementById("stat-invoices").textContent = "0";
      document.getElementById("stat-spent").textContent    = "0";
    }
  } catch(e) {
    document.getElementById("stat-active").textContent   = "-";
    document.getElementById("stat-invoices").textContent = "-";
    document.getElementById("stat-spent").textContent    = "-";
  }
}

// ==============================================================
//  LOGOUT
// ==============================================================
function logout() {
  localStorage.clear();
  window.location.href = "index.html";
}

// ==============================================================
//  INIT — check notifications silently on load, then show plans
// ==============================================================
(async () => {
  // Silently check for expiring subscriptions to update badge
  try {
    const res = await fetch(`${BASE}/customer/my-active-subscriptions`, { headers: AUTH });
    if (res.ok) {
      const subs = await res.json();
      const now  = new Date();
      const expCount = subs.filter(s => {
        const days = Math.ceil((new Date(s.end_date) - now) / 86400000);
        return days <= 7;
      }).length;
      if (expCount > 0) {
        const badge = document.getElementById("notif-count-badge");
        badge.textContent = expCount;
        badge.style.display = "inline-flex";
      }
    }
  } catch(e) { /* silent */ }

  loadPlans();
})();
