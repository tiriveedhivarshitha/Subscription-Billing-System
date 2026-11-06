with open("dashboard.js", "r", encoding="utf-8") as f:
    js = f.read()

# Add loadPlans function
load_plans_js = """
// CUSTOMER FEATURE: Load Plan Cards
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
    // Navigate to upgrade section and pre-fill the plan
    showSection('upgrade');
    const select = document.getElementById('newPlanSelect');
    if(select) {
        // Find if option exists
        let exists = false;
        for(let i=0; i<select.options.length; i++) {
            if(select.options[i].value === planId) exists = true;
        }
        if(!exists) {
            // Add it dynamically if not in the basic dropdown
            const opt = document.createElement('option');
            opt.value = planId;
            opt.text = planId;
            select.appendChild(opt);
        }
        select.value = planId;
    }
}
"""

if "loadPlans()" not in js:
    # insert before originalShowSection intercept
    js = js.replace("showSection = function(sectionId) {", load_plans_js + "\nshowSection = function(sectionId) {")
    js = js.replace("if (sectionId === 'metrics') loadMetrics();", "if (sectionId === 'metrics') loadMetrics();\n    if (sectionId === 'plan_cards') loadPlans();")

with open("dashboard.js", "w", encoding="utf-8") as f:
    f.write(js)
