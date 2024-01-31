var indices=[];
var currentPage = 0;
var size_by_page = 100;
var full_length = 0;
var asc=true;
var sorted_index=0;
var is_int=[];
const data = JSON.parse(document.getElementById('mydata').textContent);

function create_table(){
    var query= document.getElementById('qr');
    query.textContent="Query Searched: "+data['query'];
    
    var table=document.createElement('table');
    table.id='resultTable';
    var th=document.createElement('thead');
    var tr_th=document.createElement('tr');
    tr_th.id="col";
    var i=0;
    for(var key in data){
        if(key != "type" && key != "query"){
             var th_key=document.createElement('th');
            th_key.textContent=key;
            (function (index) {
                    th_key.onclick = function () {
                        sortTable(index);
                    };
            })(i);
            i=i+1;
            tr_th.append(th_key);
        }
     }
    th.append(tr_th);
    table.append(th);

    document.getElementById('body').append(query);

    if(data[Object.keys(data)[1]].length==0){
        var bad=document.createElement('h4');
        bad=document.textContent="No result for your query."

        document.getElementById('body').append(bad);
    }
    nb_res=document.createElement('h4');
    nb_res.textContent=data[Object.keys(data)[1]].length + " found"
    document.getElementById('body').append(nb_res);
    document.getElementById('body').append(table);
}
function DisplayResult(start,end,index){  
    table=document.getElementById('resultTable');
    for (var i = table.childNodes.length - 1; i >= 0; i--) {
        var node = table.childNodes[i];
        if (node.name === 'tf_row') {
            table.removeChild(node);
        }
    }
    if(data["type"]=="Genome"){
        is_int=[false,false,false,true,true];
        for(let i=start; i < end; i ++){

            var tf=document.createElement('tr');
            tf.name="tf_row";    
                var id = document.createElement('td');
                var link = document.createElement('a');
                link.textContent = data['Id'][index[i]];
                link.href = './Genome/'+link.textContent;
                id.appendChild(link)
                //id.textContent=data['Id'][index[i]];

                var commentary = document.createElement('td');
                commentary.textContent=data['Commentary'][index[i]];

                var chrs = document.createElement('td');
                chrs.textContent=data['#Chromosome'][index[i]];

                var length = document.createElement('td');
                length.textContent=data['Length'][index[i]];

                var species = document.createElement('td');
                species.textContent=data['Species'][index[i]];

                tf.append(id);
                tf.append(commentary);
                tf.append(species);
                tf.append(chrs);
                tf.append(length);

                table.append(tf);
            }
    }
    else if(data["type"]=="Chromosome"){
        is_int=[false,true,true,true,false,false];
        for(let i=start; i < end; i ++){

                var tf=document.createElement('tr');
                tf.name="tf_row"; 
                var id = document.createElement('td');

                var link_id = document.createElement('a');
                link_id.textContent = data['Id'][index[i]];
                link_id.href = './Genome/'+data['Genome id'][index[i]]+'/'+link_id.textContent;
                id.appendChild(link_id)

                var genome_id = document.createElement('td');
                var link = document.createElement('a');
                link.textContent = data['Genome id'][index[i]];
                link.href = './Genome/'+link.textContent;
                genome_id.appendChild(link)

                var start = document.createElement('td');
                start.textContent=data['Start'][index[i]];
                var end = document.createElement('td');
                end.textContent=data['End'][index[i]];

                var length = document.createElement('td');
                length.textContent=data['Length'][index[i]];

                var species = document.createElement('td');
                species.textContent=data['Species'][index[i]];

                tf.append(id);
                tf.append(start);
                tf.append(end);
                tf.append(length);
                tf.append(genome_id);
                tf.append(species);
                

                table.append(tf);
            }
        }
    else if(data["type"]=="Annotation"){
        is_int=[false,false,-1,true];
        console.log(start,end)
        for(let i=start; i < end; i ++){
            
            var tf=document.createElement('tr');
            tf.name="tf_row";
                        
            var id = document.createElement('td');
            var link = document.createElement('a');
            link.textContent = data['Accession'][index[i]];
            link.href = './Annotation/'+link.textContent;
            id.appendChild(link)

            var commentary = document.createElement('td');
            commentary.textContent=data['Commentary'][index[i]];

            var all_tag = document.createElement('td');
            for(let tag_index=0;tag_index<(data['Tags'][index[i]]).length;tag_index++){
                var sp=document.createElement('span');
                var link_tag = document.createElement('a');
                link_tag.textContent = data['Tags'][index[i]][tag_index];
                link_tag.href = './Tag/'+link_tag.textContent;
                sp.appendChild(link_tag)
                all_tag.append(sp);
            }

            var pos = document.createElement('td');
            pos.textContent=data['#Position'][index[i]];

            tf.append(id);
            tf.append(commentary);
            tf.append(all_tag);
            tf.append(pos);

            table.append(tf);
        }
    }
    else if(data["type"]=="Peptide"){
        is_int=[false,false,-1,true];
        for(let i=start; i < end; i++){
            var tf=document.createElement('tr');
            tf.name="tf_row";         
            var id = document.createElement('td');
            var link = document.createElement('a');
            link.textContent = data['Accession'][index[i]];
            link.href = './Peptide/'+link.textContent;
            id.appendChild(link)

            var commentary = document.createElement('td');
            commentary.textContent=data['Commentary'][index[i]];

            var all_tag = document.createElement('td');
            for(let tag_index=0;tag_index<data['Tags'][index[i]].length;tag_index++){
                var sp=document.createElement('span');
                sp.textContent=data['Tags'][index[i]][tag_index];
                all_tag.append(sp);
            }

            var len = document.createElement('td');
            len.textContent=data['Length'][index[i]];

            tf.append(id);
            tf.append(commentary);
            tf.append(all_tag);
            tf.append(len);

            table.append(tf);
        }
    }  
}

function sortTable(ColumnIndex){
    columns=document.getElementById("col");
    if (is_int[ColumnIndex]==-1){
        return;
    }
    if(sorted_index==ColumnIndex){
        
        if(asc){
            if(columns.children[ColumnIndex].textContent[0]=="("){
                columns.children[ColumnIndex].textContent="(↓)"+columns.children[ColumnIndex].textContent.slice(3);
            }
            else{
                columns.children[ColumnIndex].textContent="(↓)"+columns.children[ColumnIndex].textContent;
            }
            if(is_int[ColumnIndex]){
                indices=getSortedIndices_int(data[Object.keys(data)[ColumnIndex+1]],'desc');
            }
            else{
                indices=getSortedIndices(data[Object.keys(data)[ColumnIndex+1]],'desc');
            }
            
        }
        else{
            columns.children[ColumnIndex].textContent="(↑)"+columns.children[ColumnIndex].textContent.slice(3);
            if(is_int[ColumnIndex]){
                indices=getSortedIndices_int(data[Object.keys(data)[ColumnIndex+1]],'asc');
            }
            else{
            indices=getSortedIndices(data[Object.keys(data)[ColumnIndex+1]],'asc');
            }
        }
        asc=!asc;
    }
    else{
        if(is_int[ColumnIndex]){
            indices=getSortedIndices_int(data[Object.keys(data)[ColumnIndex+1]],'asc');
        }
        else{
        indices=getSortedIndices(data[Object.keys(data)[ColumnIndex+1]],'asc');
        }
        if(columns.children[sorted_index].textContent[0]=="("){
            columns.children[sorted_index].textContent=columns.children[sorted_index].textContent.slice(3);
        }
        columns.children[ColumnIndex].textContent="(↑)"+columns.children[ColumnIndex].textContent;
        sorted_index=ColumnIndex;
        asc=true;
    }
    DisplayResult(currentPage*size_by_page,Math.min(full_length,(currentPage+1)*size_by_page-1),indices) 
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
        DisplayResult(currentPage*size_by_page,Math.min(full_length+1,(currentPage+1)*size_by_page-1),indices) // Change the column index as needed
        document.getElementById("currentPage").textContent=currentPage+1;
        document.getElementById("currentPage2").textContent=currentPage+1;
    }
}

function nextPage() {
    if ((currentPage+1)*size_by_page <= full_length) {
        currentPage++;
        DisplayResult(currentPage*size_by_page,Math.min(full_length+1,(currentPage+1)*size_by_page-1),indices) // Change the column index as needed
        document.getElementById("currentPage").textContent=currentPage+1;
        document.getElementById("currentPage2").textContent=currentPage+1;
    }
}
document.addEventListener('DOMContentLoaded', function() {
    create_table();
    indices=getSortedIndices(data[Object.keys(data)[1]]);
    full_length=indices.length-1
    console.log("fulll lenght",full_length)
    DisplayResult(0,Math.min(size_by_page,full_length+1),indices);
});