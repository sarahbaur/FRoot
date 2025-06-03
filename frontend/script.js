document.addEventListener('DOMContentLoaded', () => {
    // Check if the overlay was already dismissed in this session
    if (!sessionStorage.getItem('overlayDismissed')) {
        // Start overlay functionality
        const startOverlay = document.createElement('div');
        startOverlay.id = 'start-overlay';
        startOverlay.style.position = 'fixed';
        startOverlay.style.top = '0';
        startOverlay.style.left = '0';
        startOverlay.style.width = '100%';
        startOverlay.style.height = '100%';
        startOverlay.style.backgroundColor = '#FFFFFF'; // Your choice of color
        startOverlay.style.zIndex = '1000'; // Ensure this is above all other content
        startOverlay.style.display = 'flex';
        startOverlay.style.justifyContent = 'center';
        startOverlay.style.alignItems = 'center';
        startOverlay.style.opacity = '1';
        startOverlay.style.transition = 'opacity 2s ease'; // Transition for smooth effect; changed to 2s for a slower transition
        startOverlay.innerHTML = '<div class="brand-container"><span class="brand_name">FR<span class="brand_name_small">oot</span></span></div>';
        document.body.appendChild(startOverlay);

        // Listen for clicks on the overlay to start the app
        startOverlay.addEventListener('click', () => {
            // Start the fade out
            startOverlay.style.opacity = '0';

            // Wait for the transition to finish before setting display to 'none'
            setTimeout(() => {
                startOverlay.style.display = 'none';
            }, 1000); // changed to 2000ms to match the 2s transition duration

            // Set a flag in sessionStorage to indicate the overlay has been dismissed
            sessionStorage.setItem('overlayDismissed', 'true');
        });
    }

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // Select submit button elements
    const submitButton = document.querySelector('button[type="submit"]');
    const loadingSpinners = document.querySelectorAll('.spinner'); // Selects all spinners

    // Event listener for form submission
    const form = document.getElementById('wordQueryForm');
    form.addEventListener('submit', (event) => {
        event.preventDefault();

        // Display loading spinners and disable the submit button
        loadingSpinners.forEach(spinner => spinner.style.display = 'block');
        submitButton.disabled = true;

        const lemmaInput = document.getElementById('lemmaInput');
        const meaningInput = document.getElementById('meaningInput');

        // Update span texts
        document.getElementById('inputLemma').textContent = lemmaInput.value;
        document.getElementById('inputMeaning').textContent = meaningInput.value;

        // Prepare request data
        const requestData = {
            lemma: lemmaInput.value,
            meaning: meaningInput.value
        };

         fetch('/process-query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', // Set the content type to application/json
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Received data:', data);  // Logging the received data
            updateResults('.lemmaResults', data.lemma_results, true);
            updateResults('.meaningResults', data.meaning_results, false);
        })
        .catch(error => {
            console.error('Error:', error);
            document.querySelector('.analyzationDiv').textContent = 'Error: Could not process query.';
        })
        .finally(() => {
            loadingSpinners.forEach(spinner => spinner.style.display = 'none');
            submitButton.disabled = false;
        });
        // Clear input fields and previous results
        lemmaInput.value = '';
        meaningInput.value = '';
        document.querySelector('.lemmaResults').innerHTML = '';
        document.querySelector('.meaningResults').innerHTML = '';
    });

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // Function to update results list in the UI
    function updateResults(selector, results, isLemma) {
        const resultsElement = document.querySelector(selector);
        // Clear any existing results
        resultsElement.innerHTML = '';

        // Check if results have exactly 5 elements
        if (results && results.length === 5) {
            const list = document.createElement('ol');
            results.forEach(result => {
                appendListItem(list, result, isLemma);
            });
            resultsElement.appendChild(list);
        } else {
            // Handle the case where there are not exactly 5 results
            // For example, display a message or log an error
            console.error('Expected 5 results, but got:', results.length);
            resultsElement.innerHTML = '<p>Error: Expected 5 results but did not receive them.</p>';
        }
    }

    // Function to create and append list item with click listener for more info
    function appendListItem(listElement, result, isLemma) {
        if (!result || isNaN(parseFloat(result.score))) {
            console.error('Invalid result data:', result);
            return;
        }

        const item = document.createElement('li');
        item.textContent = constructTextContent(result, isLemma);
        item.style.width = `${Math.max(5, parseFloat(result.score) * 100)}%`;
        item.classList.add(isLemma ? 'lemmaResultsContainer' : 'meaningResultsContainer');
        item.dataset.id = result.id;

        item.addEventListener('click', () => {
            toggleMoreInfo(item, result.id);
        });

        listElement.appendChild(item);
    }

    // Function to clean up improperly encoded characters
    function cleanUpEncodedCharacters(text) {
        // Replace improperly encoded characters with their correct counterparts
        text = text.replace(/\\u00e9/g, "é");
        text = text.replace(/\\u00e8/g, "è");
        text = text.replace(/\\u00ea/g, "ê");
        text = text.replace(/\\u00eb/g, "ë");
        text = text.replace(/\\u00e7/g, "ç");
        text = text.replace(/\\u00e0/g, "à");
        text = text.replace(/\\u00e2/g, "â");
        text = text.replace(/\\u00e4/g, "ä");
        text = text.replace(/\\u00f9/g, "ù");
        text = text.replace(/\\u00fb/g, "û");
        text = text.replace(/\\u00fc/g, "ü");
        text = text.replace(/\\u00f4/g, "ô");
        text = text.replace(/\\u00f6/g, "ö");
        text = text.replace(/\\u00ee/g, "î");
        text = text.replace(/\\u00ef/g, "ï");
        text = text.replace(/\\u0153/g, "œ");
        text = text.replace(/\\u00e6/g, "æ");
        text = text.replace(/\\u00e1/g, "á");
        text = text.replace(/\\u00ed/g, "í");
        text = text.replace(/\\u00f3/g, "ó");
        text = text.replace(/\\u00fa/g, "ú");
        text = text.replace(/\\u2019/g, "'");

        return text;
    }

    // Function to construct text content for list item with cleaned up characters
    function constructTextContent(result, isLemma) {
        let textContent = isLemma
            ? `Lemma: ${cleanUpEncodedCharacters(result.lemma)}, Score: ${result.score.toFixed(2)}`
            : `Meaning: ${cleanUpEncodedCharacters(result.sense)}, Score: ${result.score.toFixed(2)}`;

        if (result.meaning) {
            textContent += `, Meaning: ${cleanUpEncodedCharacters(result.meaning)}`;
        }

        return textContent;
    }

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // Function to handle clicking on a list item for more information
    function toggleMoreInfo(item, id) {
        const detailEndpoint = `/details/${id}`;
        const moreInfoDiv = item.querySelector('.more-info');

        if (!moreInfoDiv) {
            fetch(detailEndpoint, { method: 'GET', headers: { 'Content-Type': 'application/json' } })
            .then(response => response.json())
            .then(moreInfoData => {
                if (moreInfoData.error) {
                    console.error(`Error: ${moreInfoData.error}`);
                    return;
                }

                // Clean up the meaning before displaying it
                const cleanedMeaning = cleanUpEncodedCharacters(moreInfoData.meaning);

                appendMoreInfo(item, `
                    <div>
                        <p><strong>Lemma</strong>: ${moreInfoData.lemma}</p>
                        <p><strong>Meaning</strong>: ${cleanedMeaning}</p>
                        <p><strong>Etymology</strong>: ${moreInfoData.etymology}</p>
                    </div>
                `);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        } else {
            moreInfoDiv.style.display = moreInfoDiv.style.display === 'none' ? 'block' : 'none';
        }

        item.classList.toggle('active');
    }

    // Function to create and append more info content
    function appendMoreInfo(parentElement, htmlContent) {
        const moreInfoDiv = document.createElement('div');
        moreInfoDiv.innerHTML = htmlContent;
        moreInfoDiv.classList.add('more-info');
        parentElement.appendChild(moreInfoDiv);
    }

});

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Code to make fruits fall down the page when it is first loaded
document.addEventListener("DOMContentLoaded", function() {
    if (!sessionStorage.getItem('overlayDismissed')) {

        const fruitTypes = ['apple', 'banana', 'pear', 'peach']; // Define the types of fruits
        const totalFruits = 60; // Total number of fruits you want initially
        const animationDuration = 7; // Maximum duration of fall in seconds
        const fadeDuration = 1000; // Duration of fade out in milliseconds

        // Create a container for fruits
        const container = document.createElement('div');
        container.id = 'fruit-container';
        container.style.position = 'fixed';
        container.style.top = '0';
        container.style.left = '0';
        container.style.width = '100vw';
        container.style.height = '100vh';
        container.style.zIndex = '1000'; // Ensure this is above content but below interactive elements
        container.style.pointerEvents = 'none'; // Allows clicks to pass through
        document.body.appendChild(container);

        // Array to hold all fruit elements
        let fruits = [];

        // Create fruit elements
        for (let i = 0; i < totalFruits; i++) {
            let fruitDiv = document.createElement('div');
            fruitDiv.className = `fruit ${fruitTypes[i % fruitTypes.length]}`; // Cycle through fruit types
            fruitDiv.style.width = '70px'; // Size of the fruit
            fruitDiv.style.height = '70px';
            fruitDiv.style.position = 'absolute';
            fruitDiv.style.backgroundSize = 'contain';
            fruitDiv.style.backgroundRepeat = 'no-repeat';
            fruitDiv.style.left = `${Math.random() * 100}vw`; // Random position across the screen
            fruitDiv.style.transform = 'translateY(-100px)'; // Start position for animation

            // Assign background images based on fruit type
            switch (fruitTypes[i % fruitTypes.length]) {
                case 'apple':
                    fruitDiv.style.backgroundImage = "url('/frontend/images/apple.png')";
                    break;
                case 'banana':
                    fruitDiv.style.backgroundImage = "url('/frontend/images/banana.png')";
                    break;
                case 'pear':
                    fruitDiv.style.backgroundImage = "url('/frontend/images/pear.png')";
                    break;
                case 'peach':
                    fruitDiv.style.backgroundImage = "url('/frontend/images/peach.png')";
                    break;
                default:
                    // Handle unexpected cases or add a default fruit
                    break;
            }

            // Stagger the animation delay to ensure a constant flow
            let delay = (animationDuration / totalFruits) * i;
            fruitDiv.style.animation = `fall ${animationDuration}s ${delay}s infinite`;

            // Add fruit to the array and to the container
            fruits.push(fruitDiv);
            container.appendChild(fruitDiv);
        }

        // Listener for any click on the page
        document.addEventListener("click", function() {
            fruits.forEach(fruit => {
                // Reduce the opacity to 0 over fadeDuration milliseconds
                fruit.style.transition = `opacity ${fadeDuration}ms`;
                fruit.style.opacity = '0';

                // After the transition is complete, set display to 'none'
                setTimeout(() => {
                    fruit.style.display = 'none';
                }, fadeDuration);
            });

            // Set a flag in sessionStorage to indicate the overlay has been dismissed
            sessionStorage.setItem('overlayDismissed', 'true');
        });
    }
});
