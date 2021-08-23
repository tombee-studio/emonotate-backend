function getSignedRequest(file){
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/api/sign_s3?file_name="+file.name+"&file_type="+file.type);
    var submitButton = document.getElementById('submit-button');
    xhr.onreadystatechange = function(){
        if(xhr.readyState === 4){
            if(xhr.status === 200){
                var response = JSON.parse(xhr.responseText);
                uploadFile(file, response.data, response.url);
            }
            else{
                alert("Could not get signed URL.");
            }
        }
    };
    xhr.send();
}

function uploadFile(file, s3Data, url){
    var xhr = new XMLHttpRequest();
    xhr.upload.addEventListener('progress', (evt) => {
        let percent = (evt.loaded / evt.total * 100).toFixed(1);
        console.log(`++ xhr.upload: progress ${percent}%`);
    });
    xhr.open("POST", s3Data.url);

    var postData = new FormData();
    for(key in s3Data.fields){
        postData.append(key, s3Data.fields[key]);
    }
    postData.append('file', file);

    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4){
            if(xhr.status === 200 || xhr.status === 204){
                document.getElementById("id_movie").value = encodeURI(url);
            }
            else{
                alert("Could not upload file.");
            }
        }
    };
    xhr.send(postData);
}

window.onload = function() {
    const fileComponent = document.getElementById('id_file');
    const movieComponent = document.getElementById('id_movie');
    if(!fileComponent) throw "NOT EXISTING FILE FORM";
    if(!movieComponent) throw "NOT EXISTING URL FORM";

    fileComponent.onchange = function() {
        var files = document.getElementById("id_file").files;
        var file = files[0];
        if(!file){
            return alert("No file selected.");
        }
        getSignedRequest(file);
    };
}
