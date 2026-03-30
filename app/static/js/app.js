// TurfOps — minimal JS helpers (most interactivity via HTMX)

// Auto-dismiss flash alerts after 5 seconds
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".alert-dismissible").forEach(function (el) {
        setTimeout(function () {
            var alert = bootstrap.Alert.getOrCreateInstance(el);
            alert.close();
        }, 5000);
    });
});

// Close offcanvas sidebar on nav click (mobile)
document.addEventListener("click", function (e) {
    var link = e.target.closest(".sidebar .nav-link:not(.disabled)");
    if (!link) return;
    var offcanvas = bootstrap.Offcanvas.getInstance(document.getElementById("sidebar"));
    if (offcanvas) offcanvas.hide();
});
