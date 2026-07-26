/**
 * upload.js
 * Handles drag-and-drop file selection, filename preview, client-side
 * validation, and the loading overlay for the resume upload page.
 */

document.addEventListener("DOMContentLoaded", function () {
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("resumeInput");
    const dropzoneContent = document.getElementById("dropzoneContent");
    const fileSelected = document.getElementById("fileSelected");
    const fileNameDisplay = document.getElementById("fileNameDisplay");
    const analyzeForm = document.getElementById("analyzeForm");
    const submitBtn = document.getElementById("submitBtn");
    const loadingOverlay = document.getElementById("loadingOverlay");

    const ALLOWED_EXTENSIONS = ["pdf", "docx"];
    const MAX_SIZE_BYTES = 8 * 1024 * 1024; // 8 MB

    function getExtension(filename) {
        return filename.split(".").pop().toLowerCase();
    }

    function showSelectedFile(file) {
        fileNameDisplay.textContent = file.name;
        dropzoneContent.classList.add("d-none");
        fileSelected.classList.remove("d-none");
    }

    function resetDropzone() {
        dropzoneContent.classList.remove("d-none");
        fileSelected.classList.add("d-none");
        fileInput.value = "";
    }

    function validateAndAssign(file) {
        if (!file) return;

        const ext = getExtension(file.name);
        if (!ALLOWED_EXTENSIONS.includes(ext)) {
            alert("Invalid file type. Please upload a PDF or DOCX file.");
            resetDropzone();
            return;
        }

        if (file.size > MAX_SIZE_BYTES) {
            alert("File is too large. Please upload a file smaller than 8 MB.");
            resetDropzone();
            return;
        }

        showSelectedFile(file);
    }

    // Handle click-to-browse (native input change event)
    if (fileInput) {
        fileInput.addEventListener("change", function () {
            if (fileInput.files && fileInput.files[0]) {
                validateAndAssign(fileInput.files[0]);
            }
        });
    }

    // Drag & drop handlers
    if (dropzone) {
        ["dragenter", "dragover"].forEach(function (eventName) {
            dropzone.addEventListener(eventName, function (e) {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add("dragover");
            });
        });

        ["dragleave", "drop"].forEach(function (eventName) {
            dropzone.addEventListener(eventName, function (e) {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove("dragover");
            });
        });

        dropzone.addEventListener("drop", function (e) {
            const dt = e.dataTransfer;
            if (dt && dt.files && dt.files.length) {
                fileInput.files = dt.files;
                validateAndAssign(dt.files[0]);
            }
        });
    }

    // Show loading overlay + disable button on submit
    if (analyzeForm) {
        analyzeForm.addEventListener("submit", function (e) {
            if (!fileInput.files || !fileInput.files[0]) {
                e.preventDefault();
                alert("Please select a resume file (PDF or DOCX) before submitting.");
                return;
            }

            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing...';
            if (loadingOverlay) {
                loadingOverlay.classList.remove("d-none");
            }
        });
    }
});
