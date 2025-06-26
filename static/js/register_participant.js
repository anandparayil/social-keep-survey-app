console.log("Register Participant JS Loaded");

async function registerParticipant() {
  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const button = document.querySelector("button[onclick='registerParticipant()']");

  // Basic validation
  if (!name || !email) {
    alert("Please fill in both name and email.");
    return;
  }

  // Email format validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    alert("Please enter a valid email address.");
    return;
  }

  // Disable the button and show spinner
  button.disabled = true;
  button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Registering...`;

  const payload = { name, email };

  try {
    const response = await fetch("/admin/register_participant", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const result = await response.json();

    if (result.success) {
      alert(`🎉 ${result.message}`);
      document.getElementById("participant-form").reset();
    } else {
      alert(`❌ ${result.message}`);
    }

  } catch (error) {
    console.error("Error registering participant:", error);
    alert("Something went wrong while registering the participant.");
  } finally {
    // Reset the button
    button.disabled = false;
    button.innerHTML = `<i class="fas fa-user-check"></i> Register Participant`;
  }
}
