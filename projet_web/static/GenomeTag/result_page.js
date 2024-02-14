var indices = [];
var currentPage = 0;
var size_by_page = 100;
var full_length = 0;
var asc = true;
var sorted_index = 0;
var is_int = [];
const data = JSON.parse(document.getElementById('mydata').textContent);

var pageContainer = document.getElementById('container');


// Your dynamic content generation
//var dynamicContent = document.createElement('p');
var skipLine = document.createElement('br');


function create_table() {
    var query = document.getElementById('qr');

    query.textContent = "Query Searched: " + data['query'];
    pageContainer.append(pagination);
    //pageContainer.append(query.textContent);
    var bodyElement = document.getElementById('body');

    // Check if there are results
    if (data[Object.keys(data)[1]].length > 0) {
        //console.log("i am here");
        var table = document.createElement('table');
        table.className = 'table table-hover';
        table.id = 'resultTable';

        var th = document.createElement('thead');
        var tr_th = document.createElement('tr');
        tr_th.id = "col";
        tr_th.id.scopeName = "col";
        var i = 0;

        for (var key in data) {
            if (key != "type" && key != "query") {
                var th_key = document.createElement('th');
                th_key.textContent = key;
                th_key.className = "table-active";

                (function (index) {
                    th_key.onclick = function () {
                        sortTable(index);
                    };
                })(i);

                i = i + 1;
                tr_th.append(th_key);
            }
        }

        th.append(tr_th);
        table.append(th);

        //bodyElement.append(query);
        nb_res = document.createElement('h4');
        nb_res.textContent = data[Object.keys(data)[1]].length + " found";
        pageContainer.append(nb_res.textContent);
        //bodyElement.append(nb_res.textContent);
        bodyElement.append(table);
        
    } else {
        // Display a message when there are no results
        var bad = document.createElement('h4');
        bad.textContent = "No result for your query.";
        pageContainer.append(skipLine);
        pageContainer.append(bad.textContent);
        //bodyElement.append(bad);
    }
   // pageContainer.append(table);
}
    function DisplayResult(start, end, index) {
        table = document.getElementById('resultTable');
        for (var i = table.childNodes.length - 1; i >= 0; i--) {
            var node = table.childNodes[i];
            if (node.name === 'tf_row') {
                table.removeChild(node);
            }
        }
        if (data["type"] == "Genome") {
            is_int = [false, false, false, true, true];
            for (let i = start; i < end; i++) {
    
                var tf = document.createElement('tr');
                tf.name = "tf_row";
    
                var id = document.createElement('td');
                var link = document.createElement('a');
                link.textContent = data['Id'][index[i]];
                link.href = './Genome/' + link.textContent;
                link.style.padding = "0"; // Set padding to 0
                link.style.margin = "0";
                link.style.backgroundColor = "#f0f0f0";
                id.appendChild(link);
                //id.className = "table-active"; // Bootstrap class
                id.scopeName = "col";
                var commentary = document.createElement('td');
                //commentary.tex
                commentary.textContent = data['Commentary'][index[i]].trim().slice(0,50)+"...";

    
                var chrs = document.createElement('td');
                chrs.textContent = data['#Chromosome'][index[i]];
    
                var length = document.createElement('td');
                length.textContent = data['Length'][index[i]];
    
                var species = document.createElement('td');
                species.textContent = data['Species'][index[i]];
    
                tf.append(id);
                tf.append(commentary);
                tf.append(species);
                tf.append(chrs);
                tf.append(length);
    
                tf.className = "table-active"; // Bootstrap class
                table.append(tf);
            }
        }
        else if (data["type"] == "Chromosome") {
            is_int = [false, true, true, true, false, false];
            for (let i = start; i < end; i++) {
                var tf = document.createElement('tr');
                tf.name = "tf_row";
    
                var id = document.createElement('td');
                var link_id = document.createElement('a');
                link_id.textContent = data['Id'][index[i]];
                link_id.href = './Genome/' + data['Genome id'][index[i]] + '/' + link_id.textContent;
                link_id.style.padding = "0"; // Set padding to 0
                link_id.style.margin = "0";
                link_id.style.backgroundColor = "#f0f0f0";
                
                id.appendChild(link_id);
                
                id.scopeName = "col";
                var genome_id = document.createElement('td');
                var link = document.createElement('a');
                link.textContent = data['Genome id'][index[i]];
                link.href = './Genome/' + link.textContent;
                link.style.padding = "0"; // Set padding to 0
                link.style.margin = "0";
                link.style.backgroundColor = "#f0f0f0";
                genome_id.appendChild(link);
    
                var start_pos = document.createElement('td');
                start_pos.textContent = data['Start'][index[i]];
    
                var end_pos = document.createElement('td');
                end_pos.textContent = data['End'][index[i]];
    
                var length = document.createElement('td');
                length.textContent = data['Length'][index[i]];
    
                var species = document.createElement('td');
                species.textContent = data['Species'][index[i]];
    
                tf.append(id);
                tf.append(start_pos);
                tf.append(end_pos);
                tf.append(length);
                tf.append(genome_id);
                tf.append(species);
                
                table.append(tf);
            }
        }
        else if (data["type"] == "Annotation") {
            is_int = [false, false, -1, true,false];
            console.log(start, end)
            for (let i = start; i < end; i++) {
    
                var tf = document.createElement('tr');
                tf.name = "tf_row";
    
                var id = document.createElement('td');
                var link = document.createElement('a');
                link.textContent = data['Accession'][index[i]];
                link.href = './Annotation/' + link.textContent;
                link.style.padding = "0"; // Set padding to 0
                link.style.margin = "0";
                link.style.backgroundColor = "#f0f0f0";
                id.appendChild(link);
                //id.className = "table-active"; // Bootstrap class
                id.scopeName = "col";
                var commentary = document.createElement('td');
                commentary.textContent = data['Commentary'][index[i]].trim().slice(0,50)+"...";

    
                var all_tag = document.createElement('td');
                for (let tag_index = 0; tag_index < (data['Tags'][index[i]]).length; tag_index++) {
                    var sp = document.createElement('span');
                    var link_tag = document.createElement('a');
                    link_tag.textContent = data['Tags'][index[i]][tag_index];
                    link_tag.href = './Tag/' + link_tag.textContent;
                    link_tag.style.padding = "0"; // Set padding to 0
                link_tag.style.margin = "0";
                link_tag.style.backgroundColor = "#f0f0f0";
                    sp.appendChild(link_tag);
                    all_tag.append(sp);
                }
    
                var pos = document.createElement('td');
                pos.textContent = data['#Position'][index[i]];
                
                var stat = document.createElement('td');
                stat.textContent = data['Status'][index[i]];
    
                tf.append(id);
                tf.append(commentary);
                tf.append(all_tag);
                tf.append(pos);
                tf.append(stat);
    
                table.append(tf);
            }
        }
        else if (data["type"] == "Peptide") {
            is_int = [false, false, -1, true];
            for (let i = start; i < end; i++) {
                var tf = document.createElement('tr');
                tf.name = "tf_row";
        
                var id = document.createElement('td');
                var link = document.createElement('a');
                link.textContent = data['Accession'][index[i]];
                link.href = './Peptide/' + link.textContent;
                link.style.padding = "0"; // Set padding to 0
                link.style.margin = "0";
                link.style.backgroundColor = "#f0f0f0";
                id.appendChild(link);
                //id.className = "table-active"; // Bootstrap class
                id.scopeName = "col";
                var commentary = document.createElement('td');
                commentary.textContent = data['Commentary'][index[i]].trim().slice(0,50)+"...";;


        
                var all_tag = document.createElement('td');
                for (let tag_index = 0; tag_index < data['Tags'][index[i]].length; tag_index++) {
                    var sp = document.createElement('span');
                    sp.textContent = data['Tags'][index[i]][tag_index];
                    all_tag.append(sp);
                }
        
                var len = document.createElement('td');
                len.textContent = data['Length'][index[i]];
        
                tf.append(id);
                tf.append(commentary);
                tf.append(all_tag);
                tf.append(len);
        
                table.append(tf);
            }
        }
        pageContainer.append(table);
    }        


function sortTable(ColumnIndex) {
    columns = document.getElementById("col");
    if (is_int[ColumnIndex] == -1) {
        return;
    }
    if (sorted_index == ColumnIndex) {

        if (asc) {
            if (columns.children[ColumnIndex].textContent[0] == "(") {
                columns.children[ColumnIndex].textContent = "(↓)" + columns.children[ColumnIndex].textContent.slice(3);
            }
            else {
                columns.children[ColumnIndex].textContent = "(↓)" + columns.children[ColumnIndex].textContent;
            }
            if (is_int[ColumnIndex]) {
                indices = getSortedIndices_int(data[Object.keys(data)[ColumnIndex + 1]], 'desc');
            }
            else {
                indices = getSortedIndices(data[Object.keys(data)[ColumnIndex + 1]], 'desc');
            }

        }
        else {
            columns.children[ColumnIndex].textContent = "(↑)" + columns.children[ColumnIndex].textContent.slice(3);
            if (is_int[ColumnIndex]) {
                indices = getSortedIndices_int(data[Object.keys(data)[ColumnIndex + 1]], 'asc');
            }
            else {
                indices = getSortedIndices(data[Object.keys(data)[ColumnIndex + 1]], 'asc');
            }
        }
        asc = !asc;
    }
    else {
        if (is_int[ColumnIndex]) {
            indices = getSortedIndices_int(data[Object.keys(data)[ColumnIndex + 1]], 'asc');
        }
        else {
            indices = getSortedIndices(data[Object.keys(data)[ColumnIndex + 1]], 'asc');
        }
        if (columns.children[sorted_index].textContent[0] == "(") {
            columns.children[sorted_index].textContent = columns.children[sorted_index].textContent.slice(3);
        }
        columns.children[ColumnIndex].textContent = "(↑)" + columns.children[ColumnIndex].textContent;
        sorted_index = ColumnIndex;
        asc = true;
    }
    DisplayResult(currentPage * size_by_page, Math.min(full_length, (currentPage + 1) * size_by_page - 1), indices)
}



function getSortedIndices_int(arr, order = 'asc') {
    const comparator = (a, b) => (order === 'desc' ? parseFloat(arr[b]) - parseFloat(arr[a]) : parseFloat(arr[a]) - parseFloat(arr[b]));
    return Array.from({ length: arr.length }, (_, index) => index).sort(comparator);
}

function getSortedIndices(arr, order = 'asc') {
    const comparator = (a, b) => (order === 'desc' ? arr[b].localeCompare(arr[a]) : arr[a].localeCompare(arr[b]));
    return Array.from({ length: arr.length }, (_, index) => index).sort(comparator);
}

function prevPage() {
    if (currentPage >= 1) {
        currentPage--;
        DisplayResult(currentPage * size_by_page, Math.min(full_length + 1, (currentPage + 1) * size_by_page - 1), indices) // Change the column index as needed
        document.getElementById("currentPage").textContent = currentPage + 1;
    }
}

function nextPage() {
    if ((currentPage + 1) * size_by_page <= full_length) {
        currentPage++;
        DisplayResult(currentPage * size_by_page, Math.min(full_length + 1, (currentPage + 1) * size_by_page - 1), indices) // Change the column index as needed
        document.getElementById("currentPage").textContent = currentPage + 1;
    }
}
document.addEventListener('DOMContentLoaded', function () {
    create_table();
    indices = getSortedIndices(data[Object.keys(data)[1]]);
    full_length = indices.length - 1
    console.log("fulll length", full_length)
    DisplayResult(0, Math.min(size_by_page, full_length + 1), indices);
});