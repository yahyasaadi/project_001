$(document).ready(function() {
    let counter = 0;

    // Function to add a new input row
    function addRow() {
        counter++;
        let newRow = `
            <tr>
                <td>${counter}</td>
                <td><input type="text" class="form-control" name="name[]" placeholder="Name of the sibling"></td>
                <td>
                    <select class="form-control" name="institution[]">
                        <option value="secondary">Secondary</option>
                        <option value="college">College</option>
                        <option value="university">University</option>
                    </select>
                </td>
                <td><input type="number" class="form-control" name="fees[]" placeholder="Annual Fees (Kshs)"></td>
                <td><button type="button" class="btn btn-danger btn-remove" data-row="${counter}">Remove</button></td>
            </tr>
        `;
        $("#form-container").append(newRow);
    }

    // Function to remove a row
    $(document).on("click", ".btn-remove", function() {
        let row = $(this).data("row");
        $(`[data-row=${row}]`).closest("tr").remove();
    });

    // Event handler for "Add" button
    $("#btn-add").click(function() {
        addRow();
    });
});


function toggleTextarea() {
    var selectValue = document.getElementById("receivedCDF").value;
    var textarea = document.getElementById("additionalInfo");

    if (selectValue === "yes") {
        textarea.style.display = "block";
    } else {
        textarea.style.display = "none";
    }
}