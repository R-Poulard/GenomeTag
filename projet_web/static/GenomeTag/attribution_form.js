
function new_pos() {

    var new_field = document.createElement('fieldset');
    //SUPPRESS ASAP
    new_field.style.width = '90%';
    //to put the fields next to eachother
    new_field.style.display = 'absolute';
    // Create a select element
    var chr = document.createElement('select');
    chr.style.height="20px";
    var optionsData=document.getElementById('id_Chromosome').children;

    for (var i = 0; i < optionsData.length; i++) {
            var option = document.createElement('option');
            option.value = optionsData[i].value;
            option.text = optionsData[i].text;
            chr.appendChild(option);
    }

    chr.id = "id_Chromosome";
    chr.name="Chromosome";
    console.log(chr.name)
    var strand = document.createElement('select');
    strand.style.height="50%";
    var optionsData=document.getElementById('id_Strand').children;

    for (var i = 0; i < optionsData.length; i++) {
            var option = document.createElement('option');
            option.value = optionsData[i].value;
            option.text = optionsData[i].text;
            strand.appendChild(option);
    }

    strand.id = "id_Strand";
    strand.name="strand";
    

    var start=document.createElement('input');
    start.type='number';
    start.id="id_Start"
    start.name="Start"
    start.className = "form-label mt-4";

    var end=document.createElement('input');
    end.type='number';
    end.id="id_End"
    end.name="End"
    end.className = "form-label mt-4";
    
    new_field.append(chr);
    //new_field.innerHTML += '   ';
    new_field.append(strand);
    //new_field.innerHTML += '   ';
    new_field.append(start);
    //new_field.innerHTML += '  ';
    new_field.append(end);
    
    var supp = document.createElement('input');
    supp.value = " ";
    supp.type = "submit";
    supp.name = "delete";
    supp.className = 'btn-close';
    // Attach the event handler to the "x" button
    supp.addEventListener('click', function () {
        suppress_condition(this);
    });
    // Append the result element to the container

    
    new_field.innerHTML += '  ';
    new_field.appendChild(supp);

    var resultContainer = document.getElementById('position_form');
    var end=document.getElementById("end");
    resultContainer.insertBefore(new_field, end)
    
}






function suppress_condition(e) {
    var previousElement = e.parentNode.previousSibling;

    // Remove the element referenced by e.parentNode
    e.parentNode.parentNode.removeChild(e.parentNode);
}

document.addEventListener('DOMContentLoaded', function () {

    document.getElementById("add").addEventListener('click', function (event) {
        // Call the function defined in the external file
        new_pos(true);
        event.preventDefault();
    });
});

