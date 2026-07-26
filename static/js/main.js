/**
 * main.js
 * Global JavaScript behaviors used across all pages of ResumeIQ.
 */

document.addEventListener("DOMContentLoaded", function () {
    // Auto-dismiss flash messages after 6 seconds
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(function (alertEl) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 6000);
    });

    // Smooth scroll for in-page anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener("click", function (e) {
            const targetId = this.getAttribute("href");
            if (targetId.length > 1) {
                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: "smooth" });
                }
            }
        });
    });

    // Animate score breakdown progress bars on the result page
    const progressBars = document.querySelectorAll(".score-breakdown .progress-bar");
    if (progressBars.length) {
        progressBars.forEach(function (bar) {
            const targetWidth = bar.style.width;
            bar.style.width = "0%";
            setTimeout(function () {
                bar.style.transition = "width 1s ease";
                bar.style.width = targetWidth;
            }, 150);
        });
    }
});
