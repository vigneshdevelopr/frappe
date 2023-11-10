frappe.ui.form.on('Testing321', {
    condition: function(frm) {
        // Trigger a refresh of the Department field
        frm.refresh_field('department');
    }
});
