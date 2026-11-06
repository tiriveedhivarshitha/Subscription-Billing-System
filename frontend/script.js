// SIGNIN FETCHING THE DATA FROM FORM AND SENDING IT
const loginForm = document.getElementById("sign-in-form");
if (loginForm) {
    loginForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const email = document.getElementById("mail").value;
        const password = document.getElementById("pass").value;

        // Read selected role radio button
        const roleInput = document.querySelector('input[name="role"]:checked');
        if (!roleInput) {
            document.getElementById("message").textContent = "Please select a role (User or Admin).";
            return;
        }
        const role_type = roleInput.value;

        const data = {
            Email: email,
            Password: password,
            role_type: role_type
        };

        try {
            const response = await fetch("http://127.0.0.1:8000/auth/signin", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            // Convert FastAPI JSON response into JavaScript object
            const result = await response.json();

            // Check whether request was successful
            if (response.ok) {

                // Store JWT token and role
                localStorage.setItem("token", result.token);

                // Decode JWT to read the role
                const payload = JSON.parse(atob(result.token.split('.')[1]));
                const userRole = payload.role;

                // Save role so dashboards can auth-guard
                localStorage.setItem("role", userRole);

                // Show success message
                document.getElementById("message").textContent = "Login successful! Redirecting...";

                // Redirect based on role
                if (userRole === "admin") {
                    window.location.href = "admin-dashboard.html";
                } else {
                    window.location.href = "customer-dashboard.html";
                }

            } else {
                // Show error returned by FastAPI
                const errMsg = typeof result.detail === "string"
                    ? result.detail
                    : JSON.stringify(result.detail);
                document.getElementById("message").textContent = errMsg;
            }

        } catch (error) {
            // Network/server error
            document.getElementById("message").textContent = "Unable to connect to server";
            console.error(error);
        }

    });
}

// SIGNUP: Get data from the form and send it to the backend
const signupForm = document.getElementById("sign-up-form");

if (signupForm) {
    signupForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const name = document.getElementById("name").value;
        const email = document.getElementById("mail").value;
        const password = document.getElementById("pass").value;

        // Read selected role radio button
        const roleInput = document.querySelector('input[name="role"]:checked');
        if (!roleInput) {
            document.getElementById("message").textContent = "Please select a role (User or Admin).";
            return;
        }
        const role_type = roleInput.value;

        const signupdata = {
            Name: name,
            Email: email,
            Password: password,
            role_type: role_type
        };

        // If admin role, include the secret key
        if (role_type === "admin") {
            const secretKeyEl = document.getElementById("admin-code");
            if (!secretKeyEl || !secretKeyEl.value.trim()) {
                document.getElementById("message").textContent = "Please enter the Company Secret Key for admin signup.";
                return;
            }
            signupdata.secret_key = secretKeyEl.value.trim();
        }

        try {
            const response = await fetch("http://127.0.0.1:8000/auth/signup", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(signupdata)
            });

            // Convert response JSON into JavaScript object
            const result = await response.json();

            // Check whether signup was successful
            if (response.ok) {
                document.getElementById("message").textContent = "Signup successful. Please sign in.";
            } else {
                const errMsg = typeof result.detail === "string"
                    ? result.detail
                    : JSON.stringify(result.detail);
                document.getElementById("message").textContent = errMsg;
            }

        } catch (error) {
            document.getElementById("message").textContent = "Unable to connect to server";
            console.error(error);
        }

    });
}
