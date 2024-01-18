
var field_entity_dic={
    "Genome": ["Access Number", "Length", "Number Chromosome", "With Chromosome", "With Annotation"],
    "Chromosome": ["Access Number","Start Position", "End Position","Length","In Genome","Sequence"],
    "Peptide": ["Access Number","Sequence", "Size", "Linked to Annotation","Tag id"],
    "Annotation": ["Access Number","Start Position", "End Position","In Chromosome","In Genome","Author email","Tag id"],
};

function submitForm() {
    // Your logic to generate the result
    var result = document.getElementById('res').value;

    // Create a new element to display the result
    var resultElement = document.createElement('p');
    resultElement.textContent = result;

    // Get the container where you want to display the result
    var resultContainer = document.getElementById('result');

    // Append the result element to the container
    resultContainer.innerHTML = "Entity Searched: "+ resultElement.textContent;

    //erase query
    var searchForm = document.getElementById('search_form');

    // Iterate over child nodes and remove fieldsets
    for (var i = searchForm.childNodes.length - 1; i >= 0; i--) {
        var node = searchForm.childNodes[i];
        if (node.tagName === 'FIELDSET') {
            searchForm.removeChild(node);
        }
    }
    add_condition(false)
}

function add_condition(can_delete){

    var new_field = document.createElement('fieldset');
    //SUPPRESS ASAP
    new_field.style.width = '40%';
    // Create a select element
    var condition = document.createElement('select');

    var entity = document.getElementById('res').value;
    if ((entity in field_entity_dic )==false){
        submitForm();
        return;
    }
    else{
        optionsData=field_entity_dic[entity];
         // Loop through the optionsData and create option elements
        for (var i = 0; i < optionsData.length; i++) {
                var option = document.createElement('option');
                option.value = i;
                option.text = optionsData[i];
                condition.appendChild(option);
        }

        var value = document.createElement('input');
        value.type="text";

        var supp = document.createElement('input');
        supp.value="X";
        supp.type="submit";
        // Attach the event handler to the "x" button
        supp.addEventListener('click', function() {
                suppress_condition(this);
        });
        // Append the result element to the container
        new_field.appendChild(condition)
        new_field.innerHTML += '  ';
            

        new_field.appendChild(value)
        if( can_delete){
            new_field.innerHTML += '  ';
            new_field.appendChild(supp)
        }

        var add_button = document.getElementById('spacing');
        var resultContainer = document.getElementById('search_form');
        resultContainer.insertBefore(new_field,add_button)
    }

    
    
}

function suppress_condition(e){
    e.parentNode.parentNode.removeChild(e.parentNode);
}
