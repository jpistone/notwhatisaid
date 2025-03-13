document.addEventListener('DOMContentLoaded', () => {
    // DOM elements
    const youtubeForm = document.getElementById('youtube-form');
    const youtubeUrl = document.getElementById('youtube-url');
    const loadingMessage = document.getElementById('loading');
    const videoContainer = document.getElementById('video-container');
    const videoTitle = document.getElementById('video-title');
    const videoPlayer = document.getElementById('video-player');
    const transcriptDisplay = document.getElementById('transcript-display');
    
    // Transcript data
    let transcriptData = null;
    let wordElements = [];
    let currentWordIndex = -1;
    
    // Event listeners
    youtubeForm.addEventListener('submit', handleFormSubmit);
    videoPlayer.addEventListener('timeupdate', updateTranscript);
    
    // Handle form submission
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        const url = youtubeUrl.value.trim();
        if (!url) return;
        
        // Show loading message
        loadingMessage.classList.remove('hidden');
        videoContainer.classList.add('hidden');
        
        try {
            // Send request to process the video
            const formData = new FormData();
            formData.append('youtube_url', url);
            
            const response = await fetch('/process', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Load video and fetch transcript
                loadVideo(data);
                await fetchTranscript(data.video_id);
            } else {
                alert(`Error: ${data.error}`);
            }
        } catch (error) {
            console.error('Error processing video:', error);
            alert('An error occurred while processing the video.');
        } finally {
            loadingMessage.classList.add('hidden');
        }
    }
    
    // Load video
    function loadVideo(data) {
        videoTitle.textContent = data.video_title;
        videoPlayer.src = `/${data.video_path}`;
        videoContainer.classList.remove('hidden');
    }
    
    // Fetch transcript data
    async function fetchTranscript(videoId) {
        try {
            const response = await fetch(`/transcript/${videoId}`);
            transcriptData = await response.json();
            renderTranscript();
        } catch (error) {
            console.error('Error fetching transcript:', error);
            alert('Could not load transcript data.');
        }
    }
    
    // Render the transcript
    function renderTranscript() {
        if (!transcriptData || !transcriptData.segments) {
            transcriptDisplay.textContent = 'No transcript data available.';
            return;
        }
        
        // Clear previous content
        transcriptDisplay.innerHTML = '';
        wordElements = [];
        
        // Process each segment and word
        transcriptData.segments.forEach(segment => {
            if (!segment.words) return;
            
            segment.words.forEach(word => {
                const wordEl = document.createElement('span');
                wordEl.className = 'word';
                wordEl.textContent = word.text;
                wordEl.dataset.start = word.start;
                wordEl.dataset.end = word.end;
                
                // Add click handler to jump to specific word's timestamp
                wordEl.addEventListener('click', () => {
                    videoPlayer.currentTime = word.start;
                    videoPlayer.play();
                });
                
                transcriptDisplay.appendChild(wordEl);
                wordElements.push({
                    element: wordEl,
                    start: word.start,
                    end: word.end
                });
                
                // Add space after each word
                transcriptDisplay.appendChild(document.createTextNode(' '));
            });
        });
    }
    
    // Update the transcript highlighting based on current video time
    function updateTranscript() {
        if (!wordElements.length) return;
        
        const currentTime = videoPlayer.currentTime;
        let activeWordFound = false;
        
        // Find the current word based on timestamps
        for (let i = 0; i < wordElements.length; i++) {
            const word = wordElements[i];
            
            if (currentTime >= word.start && currentTime <= word.end) {
                // If we found a new active word
                if (currentWordIndex !== i) {
                    // Remove active class from previous word
                    if (currentWordIndex >= 0) {
                        wordElements[currentWordIndex].element.classList.remove('word-active');
                    }
                    
                    // Add active class to current word
                    word.element.classList.add('word-active');
                    currentWordIndex = i;
                    
                    // Scroll the word into view
                    word.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
                
                activeWordFound = true;
                break;
            }
        }
        
        // If no active word found, clear the current active word
        if (!activeWordFound && currentWordIndex >= 0) {
            wordElements[currentWordIndex].element.classList.remove('word-active');
            currentWordIndex = -1;
        }
    }
    
    // Find the closest word to the current time when seeking
    function findClosestWord(time) {
        if (!wordElements.length) return -1;
        
        let closestIndex = 0;
        let closestDiff = Math.abs(wordElements[0].start - time);
        
        for (let i = 1; i < wordElements.length; i++) {
            const diff = Math.abs(wordElements[i].start - time);
            if (diff < closestDiff) {
                closestDiff = diff;
                closestIndex = i;
            }
        }
        
        return closestIndex;
    }
    
    // Handle video seeking
    videoPlayer.addEventListener('seeked', () => {
        if (!wordElements.length) return;
        
        const time = videoPlayer.currentTime;
        const closestIndex = findClosestWord(time);
        
        // Clear previous active word
        if (currentWordIndex >= 0) {
            wordElements[currentWordIndex].element.classList.remove('word-active');
        }
        
        // Set new active word
        currentWordIndex = closestIndex;
        
        // Scroll to the word
        if (currentWordIndex >= 0) {
            const wordEl = wordElements[currentWordIndex].element;
            wordEl.scrollIntoView({ behavior: 'auto', block: 'center' });
        }
    }
}