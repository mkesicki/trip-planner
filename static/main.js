document.addEventListener('DOMContentLoaded', () => {
    // --- STATE MANAGEMENT ---
    const state = {
        currentStep: 0,
        tripData: {},
        steps: [] // Array of objects: { id, title, results: null | string[] }
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
        startPlanner(Object.fromEntries(params));
        navigateToStep(1); // Automatically navigate to the first step
    });

    stepperContainer.addEventListener('click', e => {
        const targetStepEl = e.target.closest('.step');
        if (!targetStepEl) return;

        const targetStepNumber = parseInt(targetStepEl.dataset.step, 10);
        const isCompleted = targetStepEl.classList.contains('completed');
        const isActive = targetStepEl.classList.contains('active');

        if (isCompleted || isActive) {
            navigateToStep(targetStepNumber);
        }
    });

    function determineSteps() {
        const steps = [];
        if (state.tripData.hotels_only !== 'on') {
            let transportIcon = '✈️'; // Default icon
            switch (state.tripData.transportStart) {
                case 'trains':
                    transportIcon = '🚆';
                    break;
                case 'cars':
                    transportIcon = '🚗';
                    break;
            }
            steps.push({ id: 'main_transport', title: 'Main Transport', icon: transportIcon, results: null });
        }
        if (state.tripData.transport_only !== 'on') {
            steps.push({ id: 'hotels', title: 'Accommodations', icon: '🏨', results: null });
        }
        if (state.tripData.hotels_only !== 'on' && (state.tripData.cars_between_places === 'on' || state.tripData.trains_between_places === 'on')) {
            steps.push({ id: 'local_transport', title: 'Local Travel', icon: '🚗', results: null });
        }
        state.steps = steps;
    }

    async function fetchStepData(stepNumber) {
        const step = state.steps[stepNumber - 1];
        if (!step) return null;

        showLoader(true);
        resultsArea.innerHTML = '';
        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ step: step.id, ...state.tripData }),
            });
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            const data = await response.json();
            step.results = data.urls; // Cache the results
            return data.urls;
        } catch (error) {
            console.error('Error fetching search results:', error);
            resultsArea.innerHTML = `<p class="error">Sorry, something went wrong. Please try again later.</p>`;
            return null;
        } finally {
            showLoader(false);
        }
    }

    function renderResults(urls) {
        if (urls === null) {
            resultsArea.innerHTML = `<p class="error">Could not load results. Please try again.</p>`;
            return;
        }
        if (urls.length === 0) {
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
                setTimeout(() => { window.open(url, '_blank'); }, index * 200);
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

    function updateUrlForStep() {
        const params = new URLSearchParams(window.location.search);
        params.set('step', state.currentStep);
        history.pushState(null, '', '?' + params.toString());
    }

    function toTitleCase(str) {
        if (!str) return '';
        return str.toLowerCase().split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }

    function updateUI() {
        // Update Stepper
        stepperContainer.innerHTML = state.steps.map((step, index) => `
            <div class="step ${index + 1 === state.currentStep ? 'active' : ''} ${index + 1 < state.currentStep ? 'completed' : ''}" data-step="${index + 1}">
                <div class="step-number">${index + 1}</div>
                <div class="step-title">${step.title}</div>
            </div>
        `).join('');

        // Update Summary Card
        const summaryTitle = document.getElementById('summary-title');
        const summaryIcon = document.getElementById('summary-icon');
        const currentStepInfo = state.steps[state.currentStep - 1];
        
        if (currentStepInfo) {
            summaryTitle.textContent = currentStepInfo.title;
            summaryIcon.textContent = currentStepInfo.icon;
        }

        // Update Buttons
        prevBtn.style.display = state.currentStep > 1 ? 'inline-block' : 'none';
        nextBtn.style.display = 'inline-block';
        nextBtn.textContent = state.currentStep === state.steps.length ? 'Finish' : 'Next';
        if (state.currentStep > state.steps.length) {
            nextBtn.style.display = 'none';
            prevBtn.style.display = 'none';
            resultsArea.innerHTML = '<h3>All done! Enjoy your trip.</h3>';
        }
    }
    
    function updateSummaryData() {
        const places = Array.isArray(state.tripData['places[]']) ? state.tripData['places[]'] : [state.tripData['places[]']];
        document.getElementById('summary-from').textContent = toTitleCase(state.tripData.fromCity);
        document.getElementById('summary-to').textContent = toTitleCase(places[places.length - 1]);
        document.getElementById('summary-dates').textContent = `${state.tripData.start.split('T')[0]} to ${state.tripData.end.split('T')[0]}`;
        document.getElementById('summary-adults').textContent = state.tripData.adults;
    }

    function showLoader(show) {
        loader.style.display = show ? 'block' : 'none';
    }

    async function navigateToStep(stepNumber) {
        if (stepNumber < 1 || stepNumber > state.steps.length + 1) {
            return;
        }
        state.currentStep = stepNumber;
        
        if (stepNumber > state.steps.length) {
            updateUI();
            updateUrlForStep();
            return;
        }

        const currentStepData = state.steps[stepNumber - 1];
        if (currentStepData.results) {
            renderResults(currentStepData.results);
        } else {
            const urls = await fetchStepData(stepNumber);
            renderResults(urls);
        }
        updateUrlForStep();
        updateUI();
    }

    nextBtn.addEventListener('click', () => navigateToStep(state.currentStep + 1));
    prevBtn.addEventListener('click', () => navigateToStep(state.currentStep - 1));

    function startPlanner(tripData) {
        state.tripData = tripData;
        // Ensure array-like fields are actually arrays
        ['places[]', 'nights[]', 'countries[]'].forEach(key => {
            if (state.tripData[key] && !Array.isArray(state.tripData[key])) {
                state.tripData[key] = [state.tripData[key]];
            }
        });

        formSection.style.display = 'none';
        plannerSection.style.display = 'block';

        determineSteps();
        updateSummaryData();
    }
    
    function handlePageLoad() {
        const params = new URLSearchParams(window.location.search);
        if (params.has('start') && params.has('end')) {
            const tripDataFromUrl = {};
            for (const [key, value] of params.entries()) {
                if (key.endsWith('[]')) {
                    if (!tripDataFromUrl[key]) tripDataFromUrl[key] = [];
                    tripDataFromUrl[key].push(value);
                } else if (key !== 'step') {
                    tripDataFromUrl[key] = value;
                }
            }
            
            startPlanner(tripDataFromUrl);
            const targetStep = parseInt(params.get('step'), 10) || 1;
            navigateToStep(targetStep);

        } else {
            updatedTime(); // Initialize form state if no params
        }
    }

    handlePageLoad();
});