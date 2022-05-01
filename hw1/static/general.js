function reveal() {
    checkbox = document.getElementById("watched_uncharted")
    question = document.getElementById("conditional_question");
    text_answer = document.getElementById("conditional_answer");

    if(checkbox.checked  == true) {
        question.style.visibility = "visible";
        text_answer.style.visibility = "visible";
    }
    else {
        question.style.visibility = "hidden";
        text_answer.style.visibility = "hidden";
    } 
}