/**
 * template_preview.js
 * Powers the "Recommended Resume Template" cards on the result page:
 * clicking a card's Preview button instantly renders a simple resume
 * preview + "Why this template?" list below, no reload.
 */
(function () {
    var SECTION_ORDERS = {
        modern_tech: ["Professional Summary", "Skills", "Projects", "Experience", "Education"],
        ats_standard: ["Professional Summary", "Experience", "Education", "Skills", "Certifications"],
        executive: ["Executive Summary", "Leadership Experience", "Key Achievements", "Education"],
    };

    var DEFAULT_REASONS = {
        modern_tech: [
            "ATS friendly and easy to scan",
            "Projects placed before Education",
            "Best for Software Engineering roles",
        ],
        ats_standard: [
            "ATS friendly and easy to scan",
            "Balanced, general-purpose section order",
            "Best for General Corporate roles",
        ],
        executive: [
            "ATS friendly with a leadership-first layout",
            "Highlights impact and scope upfront",
            "Best for Management roles",
        ],
    };

    var recommendedId = null;
    var recommendedReasons = null;

    function escapeHtml(str) {
        var div = document.createElement("div");
        div.textContent = str || "";
        return div.innerHTML;
    }

    function renderPreview(templateId, candidateName, candidateRole) {
        var container = document.getElementById("resumePreviewContainer");
        if (!container) return;

        var sections = SECTION_ORDERS[templateId] || SECTION_ORDERS.ats_standard;
        var name = candidateName || "John Doe";
        var role = candidateRole || "Candidate";

        var sectionsHtml = sections
            .map(function (title) {
                return (
                    '<div class="preview-section-title">' + escapeHtml(title) + "</div>" +
                    '<p class="text-muted small mb-2">' + escapeHtml(title) + " content goes here&hellip;</p>"
                );
            })
            .join("");

        container.innerHTML =
            '<div class="resume-preview-paper">' +
            "<h4 class='fw-bold mb-0'>" + escapeHtml(name) + "</h4>" +
            '<p class="text-primary fw-semibold mb-3">' + escapeHtml(role) + "</p>" +
            sectionsHtml +
            "</div>";

        renderWhyThisTemplate(templateId);
        container.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    function renderWhyThisTemplate(templateId) {
        var list = document.getElementById("whyTemplateList");
        if (!list) return;

        var reasons =
            templateId === recommendedId && recommendedReasons && recommendedReasons.length
                ? recommendedReasons
                : DEFAULT_REASONS[templateId] || DEFAULT_REASONS.ats_standard;

        list.innerHTML = reasons
            .map(function (reason) {
                return '<li class="mb-1"><span class="text-success me-2">&#10003;</span>' + escapeHtml(reason) + "</li>";
            })
            .join("");
    }

    function highlightActiveCard(templateId) {
        document.querySelectorAll(".template-card").forEach(function (card) {
            card.classList.toggle("is-active-preview", card.getAttribute("data-template-id") === templateId);
        });
    }

    window.initTemplateRecommendation = function (options) {
        options = options || {};
        recommendedId = options.recommendedId || null;
        recommendedReasons = options.recommendedReasons || [];

        var candidateName = options.candidateName || "John Doe";
        var candidateRole = options.candidateRole || "Candidate";

        document.querySelectorAll("[data-preview-template]").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var templateId = btn.getAttribute("data-preview-template");
                highlightActiveCard(templateId);
                renderPreview(templateId, candidateName, candidateRole);
            });
        });

        if (recommendedId) {
            highlightActiveCard(recommendedId);
            renderPreview(recommendedId, candidateName, candidateRole);
        }
    };
})();
