function updateNavDateTime() {
    const navDateTime = document.getElementById("nav-datetime");
    if (!navDateTime) return;

    const now = new Date();

    const formatted = now.toLocaleString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false
    }).replace(",", " ·");

    navDateTime.textContent = formatted;
  }

  updateNavDateTime();
  setInterval(updateNavDateTime, 60000);