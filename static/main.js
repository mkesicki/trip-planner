var nights = 0;
document.getElementById("backTimeContainer").style.display = "none";
// handle is round trip checkbox
document.getElementById("roundtrip").addEventListener("click", function() {

    if (this.checked)  {
       document.getElementById("transportEndDiv").style.display = "none";
    } else {
        document.getElementById("transportEndDiv").style.display = "inline";
    }
});

// handle is hotels only checkbox
document.getElementById("hotelsOnly").addEventListener("click", function() {

  if (this.checked)  {
     document.getElementById("transportContainer").style.display = "none";
  } else {
      document.getElementById("transportContainer").style.display = "inline";
  }
});

//handle dates update
document.getElementById("transportEnd").addEventListener("change", function(){
  if(this.value == 'cars') {
      document.getElementById("backTimeContainer").style.display = "inline";
  } else {
    document.getElementById("backTimeContainer").style.display = "none";
  }
});

//handle dates update
document.getElementById("endTime").addEventListener("change", function(){
    updatedTime();
});

document.getElementById("startTime").addEventListener("change", function(){
    updatedTime();
});

// add new place to list (click on the button)
document.getElementById("placesButton").addEventListener("click", function() {

    const countries = document.getElementById("toCountry");
    places = document.getElementsByName("places[]");

    input = document.createElement("input");
    input.type = "text";
    input.name = "places[]";
    input.placeholder = "Place to go";
    input.required = "required";

    country = document.createElement("select");
    country.name = "countries[]";

    for (var i = 0; i < countries.length; i++) {
         option = document.createElement("option");
         option.value = countries.options[i].value;
         option.textContent = countries.options[i].textContent;

         if(countries.options[i].selected) {
             option.setAttribute("selected", "selected");
         }

         country.appendChild(option);
     }

    input2 = document.createElement("input");
    input2.type = "number";
    input2.name = "nights[]";
    input2.placeholder = "Nights to stay";
    input2.required = "required";
    input2.className = "nights";
    input2.setAttribute("min", "1");

    input2.addEventListener("change", function(){
        validateNights();
    });

    button = document.createElement("button");
    button.type = "button";
    button.innerHTML = "x";

    button.addEventListener("click", function(){
        this.parentNode.parentNode.remove();
    });

    div = document.createElement("div");
    div.appendChild(input);
    div.appendChild(document.createTextNode(" "));
    div.appendChild(country);
    div.appendChild(document.createTextNode(" "));
    div.appendChild(input2);
    div.appendChild(document.createTextNode(" "));
    div.appendChild(button);

    li = document.createElement("li");
    li.appendChild(div);
    li.id = "place-" + (places.length + 1);
    li.draggable = "true";
    li.className = "drag-item";
    document.getElementById("placesList").appendChild(li);
});

// dates calculations
function updatedTime() {

    var start = new Date(document.getElementById("startTime").value);
    var end = new Date(document.getElementById("endTime").value);
    console.log("updatedTime");

    if (start instanceof Date && !isNaN(start .valueOf()) && end instanceof Date && !isNaN(end.valueOf()) ) {

        diff = end - start;
        days = Math.floor(diff / (1000 * 60 * 60 * 24)) + 1;
        document.getElementById("days").value = days;
        document.getElementById("nights").value = days - 1 ;
        nights = days - 1;
    }

    setPlacesDivVisibility();
    validateNights();
}

// toggle visibilty of places depending on nights
function setPlacesDivVisibility() {

    if (nights > 0) {
        document.getElementById("placesDiv").style.display = "block";
    } else {
        document.getElementById("placesDiv").style.display = "none";
    }
}

// drag and drop magic
// kudos https://www.w3resource.com/javascript-exercises/event/javascript-event-handling-exercise-6.php
const dragList = document.getElementById('placesList');

let draggedItem = null;

// Add event listeners for drag and drop events
dragList.addEventListener('dragstart', handleDragStart);
dragList.addEventListener('dragover', handleDragOver);
dragList.addEventListener('drop', handleDrop);

 // Drag start event handler
 function handleDragStart(event) {
    draggedItem = event.target;
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/html', draggedItem.innerHTML);
    event.target.style.opacity = '0.5';
  }

  // Drag over event handler
  function handleDragOver(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
    const targetItem = event.target;
    if (targetItem !== draggedItem && targetItem.classList.contains('drag-item')) {
      const boundingRect = targetItem.getBoundingClientRect();
      const offset = boundingRect.y + (boundingRect.height / 2);
      if (event.clientY - offset > 0) {
        targetItem.style.borderBottom = 'solid 2px #000';
        targetItem.style.borderTop = '';
      } else {
        targetItem.style.borderTop = 'solid 2px #000';
        targetItem.style.borderBottom = '';
      }
    }
  }

  // Drop event handler
  function handleDrop(event) {

    event.preventDefault();
    const targetItem = event.target;

    if (targetItem !== draggedItem && targetItem.classList.contains('drag-item')) {
      if (event.clientY > targetItem.getBoundingClientRect().top + (targetItem.offsetHeight / 2)) {
        targetItem.parentNode.insertBefore(draggedItem, targetItem.nextSibling);
      } else {
        targetItem.parentNode.insertBefore(draggedItem, targetItem);
      }
    }
    targetItem.style.borderTop = '';
    targetItem.style.borderBottom = '';
    draggedItem.style.opacity = '';
    draggedItem = null;
  }

  function validateNights() {
    console.log("validateNights");

    var nights = document.getElementsByClassName("nights");
    var submit = document.getElementById("submit");
    var totalNights = 0;

    submit.removeAttribute("disabled");
    document.getElementById("error").textContent = "";

    for (var i = 0; i < nights.length; i++) {
        totalNights += parseInt(nights[i].value);
    }

    if (totalNights > document.getElementById("nights").value) {
        submit.setAttribute("disabled", "disabled");
        document.getElementById("error").textContent = "Sum of nights cannot be greater than total nights of trip";

        return;
    }

    if (totalNights < document.getElementById("nights").value) {
        submit.setAttribute("disabled", "disabled");
        document.getElementById("error").textContent = "Sum of nights needs to be equal to total nights of trip";
    }

    document.getElementById("nightsLeft").value = document.getElementById("nights").value - totalNights;
  }