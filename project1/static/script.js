function hidePersonalProgress(result, data) {
    
    // var result = {{}}
    // var data={{data | tojson}}
    console.log(data)
    return result + data
}

function editClicked(){
    alert("Edit")
}

function navBar(){
    var element;
    if(window.location.href.includes("scores")){
        element = document.getElementById("scores");
        element.classList.add("highlight");
     }
    else if(window.location.href.includes("play")){
        element = document.getElementById("play");
        element.classList.add("highlight");
     }
    else if(window.location.href.includes("progress")){
        element = document.getElementById("progress");
        element.classList.add("highlight");
     }
     else{
        element = document.getElementById("home");
        element.classList.add("highlight");
     }
}
