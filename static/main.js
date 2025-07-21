document.addEventListener('DOMContentLoaded', () => {
    // --- STATE MANAGEMENT ---
    const state = {
        currentStep: 0,
        tripData: {},
        steps: []
    };

    // --- DOM ELEMENTS ---
    const form = document.getElementById('trip-form');
    const formSection = document.getElementById('form-section');
    const plannerSection = document.getElementById('planner-section');
    const nextBtn = document.getElementById('nextBtn');
    const prevBtn = document.getElementById('prevBtn');
    const loader = document.getElementById('loader');
    const stepperContainer = document.querySelector('.stepper');
    const resultsArea = document.getElementById('results-area');

    // --- FORM LOGIC ---
    const nightsInput = document.getElementById("nights");
    const backTimeContainer = document.getElementById("backTimeContainer");
    const carPickupPlace = document.getElementById("carPickupPlace");

    document.getElementById("roundtrip").addEventListener("click", function() {
        document.getElementById("transportEndDiv").style.display = this.checked ? "none" : "inline";
    });

    document.getElementById("hotelsOnly").addEventListener("click", function() {
        document.getElementById("transportContainer").style.display = this.checked ? "none" : "inline";
    });

    document.getElementById("transportEnd").addEventListener("change", function() {
        backTimeContainer.style.display = this.value === 'cars' ? "inline" : "none";
    });

    document.getElementById("transportStart").addEventListener("change", function() {
        const isCar = this.value === 'cars';
        carPickupPlace.style.display = isCar ? "inline" : "none";
        document.getElementById("carsBetweenPlacesContainer").style.display = isCar ? "none" : "block";
        if (isCar) document.getElementById("carsBetweenPlaces").checked = false;
    });

    document.getElementById("endTime").addEventListener("change", updatedTime);
    document.getElementById("startTime").addEventListener("change", updatedTime);

    document.getElementById("placesButton").addEventListener("click", () => {
        const countriesSelect = document.getElementById("fromCountry");
        const placesList = document.getElementById("placesList");

        const li = document.createElement("li");
        li.className = "drag-item";
        li.draggable = true;

        const div = document.createElement("div");
        div.innerHTML = `
            <input type="text" name="places[]" placeholder="Place to go" required>
            <select name="countries[]">
                ${Array.from(countriesSelect.options).map(opt => `<option value="${opt.value}" ${opt.selected ? 'selected' : ''}>${opt.textContent}</option>`).join('')}
            </select>
            <input type="number" name="nights[]" placeholder="Nights" required class="nights" min="0">
            <button type="button" class="remove-place">×</button>
        `;
        li.appendChild(div);
        placesList.appendChild(li);

        li.querySelector('.nights').addEventListener('change', validateNights);
        li.querySelector('.remove-place').addEventListener('click', function() {
            this.closest('li').remove();
            validateNights();
        });
        validateNights();
    });

    function updatedTime() {
        const start = new Date(document.getElementById("startTime").value);
        const end = new Date(document.getElementById("endTime").value);
        if (!isNaN(start) && !isNaN(end) && end > start) {
            const diff = end - start;
            const days = Math.floor(diff / (1000 * 60 * 60 * 24)) + 1;
            nightsInput.value = days - 1;
            document.getElementById("days").value = days;
        } else {
            nightsInput.value = 0;
            document.getElementById("days").value = 0;
        }
        validateNights();
    }

    function validateNights() {
        const nightsElements = document.getElementsByClassName("nights");
        const submitBtn = document.getElementById("submit");
        const errorDiv = document.getElementById("error");
        let totalNights = 0;
        let valid = true;

        errorDiv.textContent = "";
        submitBtn.disabled = false;

        Array.from(nightsElements).forEach((el, i) => {
            const nightsValue = parseInt(el.value, 10) || 0;
            if (nightsValue < 0) {
                errorDiv.textContent = "Nights cannot be negative.";
                valid = false;
            }
            if (nightsValue === 0 && i > 0 && i < nightsElements.length - 1) {
                errorDiv.textContent = "Only the first and last place can have 0 nights.";
                valid = false;
            }
            totalNights += nightsValue;
        });

        if (totalNights > parseInt(nightsInput.value, 10)) {
            errorDiv.textContent = "Sum of nights cannot be greater than total trip nights.";
            valid = false;
        }

        document.querySelectorAll(".nightsLeft").forEach(el => {
            el.value = (parseInt(nightsInput.value, 10) || 0) - totalNights;
        });

        if (!valid) {
            submitBtn.disabled = true;
        }
    }

    // --- DRAG AND DROP ---
    const dragList = document.getElementById('placesList');
    let draggedItem = null;

    dragList.addEventListener('dragstart', e => {
        draggedItem = e.target.closest('.drag-item');
        if (!draggedItem) return;
        setTimeout(() => {
            draggedItem.classList.add('dragging');
        }, 0);
    });

    dragList.addEventListener('dragend', () => {
        if (draggedItem) {
            draggedItem.classList.remove('dragging');
            draggedItem = null;
        }
    });

    dragList.addEventListener('dragover', e => {
        e.preventDefault();
        const target = e.target.closest('.drag-item');
        if (target && target !== draggedItem) {
            const rect = target.getBoundingClientRect();
            const offset = e.clientY - rect.top - (rect.height / 2);
            document.querySelectorAll('.drag-over-top, .drag-over-bottom').forEach(el => {
                el.classList.remove('drag-over-top', 'drag-over-bottom');
            });
            target.classList.add(offset > 0 ? 'drag-over-bottom' : 'drag-over-top');
        }
    });

    dragList.addEventListener('dragleave', e => {
        e.target.closest('.drag-item')?.classList.remove('drag-over-top', 'drag-over-bottom');
    });

    dragList.addEventListener('drop', e => {
        e.preventDefault();
        document.querySelectorAll('.drag-over-top, .drag-over-bottom').forEach(el => {
            el.classList.remove('drag-over-top', 'drag-over-bottom');
        });
        const target = e.target.closest('.drag-item');
        if (target && draggedItem && target !== draggedItem) {
            const rect = target.getBoundingClientRect();
            const offset = e.clientY - rect.top - (rect.height / 2);
            dragList.insertBefore(draggedItem, (offset > 0) ? target.nextSibling : target);
        }
        if (draggedItem) {
            draggedItem.classList.remove('dragging');
            draggedItem = null;
        }
    });

    // --- WIZARD AND ROUTING LOGIC ---
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const places = formData.getAll('places[]');

        if (places.length === 0 || (places.length === 1 && places[0] === '')) {
            const errorDiv = document.getElementById("error");
            errorDiv.textContent = "Please add at least one destination to the 'Places to Visit' section.";
            errorDiv.scrollIntoView();
            return;
        }

        const params = new URLSearchParams(formData);
        history.pushState(null, '', '?' + params.toString());

        state.tripData = Object.fromEntries(formData.entries());
        state.tripData['places[]'] = places;
        state.tripData['nights[]'] = formData.getAll('nights[]');
        state.tripData['countries[]'] = formData.getAll('countries[]');

        formSection.style.display = 'none';
        plannerSection.style.display = 'block';
        
        initWizard();
    });

    function determineSteps() {
        const steps = [];
        if (!state.tripData.hotels_only) {
            steps.push({ id: 'main_transport', title: 'Main Transport' });
        }
        if (!state.tripData.transport_only) {
            steps.push({ id: 'hotels', title: 'Hotels' });
        }
        if (!state.tripData.hotels_only && (state.tripData.cars_between_places || state.tripData.trains_between_places)) {
            steps.push({ id: 'local_transport', title: 'Local Transport' });
        }
        state.steps = steps;
    }

    async function fetchStepData(stepId) {
        showLoader(true);
        resultsArea.innerHTML = '';
        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ step: stepId, ...state.tripData }),
            });
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            const data = await response.json();
            renderResults(data.urls);
        } catch (error) {
            console.error('Error fetching search results:', error);
            resultsArea.innerHTML = `<p class="error">Sorry, something went wrong. Please try again later.</p>`;
        } finally {
            showLoader(false);
        }
    }

    function renderResults(urls) {
        if (!urls || urls.length === 0) {
            resultsArea.innerHTML = '<p>No search results found for this step.</p>';
            return;
        }
        let html = `<h3>${state.steps[state.currentStep - 1].title} Results</h3>`;
        html += '<p>Your browser might block the "Open All" feature. If so, you may need to allow pop-ups for this site or click each link individually.</p>';
        html += '<button class="open-all-btn">Open All in New Tabs</button>';
        html += '<ul class="results-list">';
        urls.forEach(url => {
            const hostname = new URL(url).hostname.replace('www.', '');
            const decodedUrl = decodeURIComponent(url);
            html += `
                <li class="result-item">
                    <a href="${url}" target="_blank" rel="noopener noreferrer">${hostname}</a>
                    <div class="url-container">
                        <input type="text" value="${decodedUrl}" readonly>
                        <button class="copy-btn">Copy</button>
                    </div>
                </li>
            `;
        });
        html += '</ul>';
        resultsArea.innerHTML = html;

        resultsArea.querySelector('.open-all-btn').addEventListener('click', () => {
            urls.forEach((url, index) => {
                setTimeout(() => {
                    window.open(url, '_blank');
                }, index * 200);
            });
        });

        resultsArea.querySelectorAll('.copy-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                const input = e.target.previousElementSibling;
                navigator.clipboard.writeText(input.value).then(() => {
                    button.textContent = 'Copied!';
                    setTimeout(() => { button.textContent = 'Copy'; }, 2000);
                }).catch(err => {
                    console.error('Failed to copy text: ', err);
                    input.select();
                    document.execCommand('copy');
                });
            });
        });
    }

    function updateUI() {
        stepperContainer.innerHTML = state.steps.map((step, index) => `
            <div class="step ${index + 1 === state.currentStep ? 'active' : ''} ${index + 1 < state.currentStep ? 'completed' : ''}">
                <div class="step-number">${index + 1}</div>
                <div class="step-title">${step.title}</div>
            </div>
        `).join('');

        prevBtn.style.display = state.currentStep > 1 ? 'inline-block' : 'none';
        nextBtn.style.display = 'inline-block';
        nextBtn.textContent = state.currentStep === state.steps.length ? 'Finish' : 'Next';
        if (state.currentStep > state.steps.length) {
            nextBtn.style.display = 'none';
            prevBtn.style.display = 'none';
            resultsArea.innerHTML = '<h3>All done! Enjoy your trip.</h3>';
        }
    }
    
    function updateSummary() {
        document.getElementById('summary-from').textContent = state.tripData.fromCity;
        document.getElementById('summary-to').textContent = state.tripData['places[]'][state.tripData['places[]'].length - 1];
        document.getElementById('summary-dates').textContent = `${state.tripData.start.split('T')[0]} to ${state.tripData.end.split('T')[0]}`;
        document.getElementById('summary-adults').textContent = state.tripData.adults;
    }

    function showLoader(show) {
        loader.style.display = show ? 'block' : 'none';
    }

    nextBtn.addEventListener('click', () => {
        if (state.currentStep >= state.steps.length) {
            state.currentStep++;
            updateUI();
            return;
        }
        state.currentStep++;
        fetchStepData(state.steps[state.currentStep - 1].id);
        updateUI();
    });

    prevBtn.addEventListener('click', () => {
        if (state.currentStep <= 1) return;
        state.currentStep--;
        resultsArea.innerHTML = '<p>Previously generated results are not saved. Click "Next" to search again.</p>';
        updateUI();
    });

    function initWizard() {
        determineSteps();
        updateSummary();
        if (state.steps.length > 0) {
            state.currentStep = 1;
            fetchStepData(state.steps[0].id);
            updateUI();
        } else {
            resultsArea.innerHTML = "<p>No searches were configured based on your selections.</p>";
        }
    }
    
    function handlePageLoad() {
        const params = new URLSearchParams(window.location.search);
        if (params.has('start') && params.has('end')) {
            const tripDataFromUrl = {};
            const keys = [...new Set(params.keys())];
            
            keys.forEach(key => {
                const allValues = params.getAll(key);
                tripDataFromUrl[key] = key.endsWith('[]') ? allValues : allValues[0];
            });
            state.tripData = tripDataFromUrl;

            formSection.style.display = 'none';
            plannerSection.style.display = 'block';
            
            initWizard();
        } else {
            updatedTime();
        }
    }

    handlePageLoad();
});