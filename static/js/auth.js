const toggleButtons = document.querySelectorAll(".password-toggle");

const eyeIcon = `
    <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M12 5C6.5 5 2.1 8.4 1 12c1.1 3.6 5.5 7 11 7s9.9-3.4 11-7c-1.1-3.6-5.5-7-11-7Zm0 11a4 4 0 1 1 0-8 4 4 0 0 1 0 8Zm0-2.2a1.8 1.8 0 1 0 0-3.6 1.8 1.8 0 0 0 0 3.6Z"/>
    </svg>
`;

const eyeOffIcon = `
    <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M2.3 1 1 2.3l3 3C2.7 6.7 1.6 8.2 1 10c1.1 3.6 5.5 7 11 7 2.1 0 4-.5 5.6-1.3l3.1 3.1 1.3-1.3L2.3 1Zm9.7 14c-4.2 0-7.6-2.4-8.8-5 .4-1.1 1.1-2.1 2-2.9l2 2A4 4 0 0 0 12 15Zm0-10c5.5 0 9.9 3.4 11 7-.4 1.4-1.3 2.7-2.5 3.8l-1.5-1.5A6.9 6.9 0 0 0 20.8 12C19.6 9.4 16.2 7 12 7c-1.1 0-2.1.2-3 .5L7.4 5.9C8.8 5.3 10.3 5 12 5Z"/>
    </svg>
`;

toggleButtons.forEach((toggleButton) => {
    toggleButton.innerHTML = eyeIcon;
});

toggleButtons.forEach((toggleButton) => {
    const passwordInput = document.getElementById(toggleButton.dataset.target);

    toggleButton.addEventListener("click", () => {
        const isPasswordHidden = passwordInput.type === "password";
        passwordInput.type = isPasswordHidden ? "text" : "password";
        toggleButton.innerHTML = isPasswordHidden ? eyeOffIcon : eyeIcon;
        toggleButton.setAttribute("aria-label", isPasswordHidden ? "Hide password" : "Show password");
    });
});