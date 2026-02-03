document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const addCardBtn = document.getElementById('add-card-btn');
    const saveBtn = document.getElementById('save-board-btn');
    const loadBtn = document.getElementById('load-board-btn');
    const fileInput = document.getElementById('file-input');
    const modal = document.getElementById('card-modal');
    const closeModal = document.querySelector('.close-modal');
    const cardForm = document.getElementById('card-form');
    const modalTitle = document.getElementById('modal-title');
    const cardContainers = document.querySelectorAll('.card-container');
    const cardTitleInput = document.getElementById('card-title-input');
    const cardDescInput = document.getElementById('card-description-input');
    const cardColumnSelect = document.getElementById('card-column-select');
    
    // Application State
    let nextCardId = 1;
    let currentEditCardId = null;
    let boardData = { cards: [] };

    // Initialize
    initializeBoard();

    // Event Listeners
    addCardBtn.addEventListener('click', () => openModal());
    saveBtn.addEventListener('click', exportToFile);
    loadBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', importFromFile);
    closeModal.addEventListener('click', () => closeModalFn());
    cardForm.addEventListener('submit', handleCardFormSubmit);
    
    cardContainers.forEach(container => {
        container.addEventListener('dragover', handleDragOver);
        container.addEventListener('dragleave', handleDragLeave);
        container.addEventListener('drop', handleDrop);
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) closeModalFn();
    });

    // Load from server on startup
    async function initializeBoard() {
        try {
            const response = await fetch('/api/load');
            if (response.ok) {
                boardData = await response.json();
                updateNextCardId();
                renderBoard();
                return;
            }
        } catch (err) {
            console.log('Server API not available, trying kanban.json');
        }
        
        // Fallback to static file
        try {
            const response = await fetch('kanban.json');
            if (response.ok) {
                boardData = await response.json();
                updateNextCardId();
                renderBoard();
            }
        } catch (err) {
            console.error('Error loading data:', err);
            renderBoard();
        }
    }

    // Save to server (auto-called on every change)
    async function saveToServer() {
        try {
            const response = await fetch('/api/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(boardData, null, 2)
            });
            if (!response.ok) throw new Error('Save failed');
        } catch (err) {
            console.error('Error saving to server:', err);
            // Fallback to localStorage
            localStorage.setItem('kanbanBoard', JSON.stringify(boardData));
        }
    }

    function updateNextCardId() {
        const ids = boardData.cards
            .map(c => c.id)
            .filter(id => id && id.startsWith('card-'))
            .map(id => parseInt(id.split('-')[1]));
        nextCardId = ids.length ? Math.max(...ids) + 1 : 1;
    }

    function openModal(cardId = null) {
        modalTitle.textContent = cardId ? 'Edit Card' : 'Add New Card';
        currentEditCardId = cardId;
        cardForm.reset();
        
        if (cardId) {
            const card = boardData.cards.find(c => c.id === cardId);
            if (card) {
                cardTitleInput.value = card.title;
                cardDescInput.value = card.description;
                cardColumnSelect.value = card.column;
            }
        }
        
        modal.style.display = 'block';
        cardTitleInput.focus();
    }

    function closeModalFn() {
        modal.style.display = 'none';
        currentEditCardId = null;
    }

    function handleCardFormSubmit(e) {
        e.preventDefault();
        
        const title = cardTitleInput.value.trim();
        let description = cardDescInput.value.trim();
        const column = cardColumnSelect.value;
        
        if (!title) return;
        
        const now = new Date().toISOString();
        const formattedDate = formatDate(now);
        const columnCapitalized = column.charAt(0).toUpperCase() + column.slice(1);
        
        // Clean description of any existing timestamps
        if (description.includes("📅 Created:")) {
            description = description.split("📅 Created:")[0].trim();
        }
        
        if (currentEditCardId) {
            const cardIndex = boardData.cards.findIndex(c => c.id === currentEditCardId);
            if (cardIndex !== -1) {
                const oldColumn = boardData.cards[cardIndex].column;
                
                // Only add status change if the column actually changed
                if (oldColumn !== column) {
                    // Initialize statusChanges array if it doesn't exist
                    if (!boardData.cards[cardIndex].statusChanges) {
                        boardData.cards[cardIndex].statusChanges = [];
                    }
                    
                    // Add the status change
                    boardData.cards[cardIndex].statusChanges.push({
                        from: oldColumn,
                        to: column,
                        timestamp: now
                    });
                    
                    // If no createdAt exists, add it now
                    if (!boardData.cards[cardIndex].createdAt) {
                        boardData.cards[cardIndex].createdAt = now;
                    }
                    
                    // Format the timestamps directly into the description
                    const createdTime = formatDate(boardData.cards[cardIndex].createdAt);
                    description = `${description}\n\n📅 Created: ${createdTime}\n🔄 Status: ${columnCapitalized} (${formattedDate})`;
                }
                
                boardData.cards[cardIndex] = {
                    ...boardData.cards[cardIndex],
                    title, 
                    description, 
                    column
                };
            }
        } else {
            // For new cards, add timestamps directly to description
            description = `${description}\n\n📅 Created: ${formattedDate}\n🔄 Status: ${columnCapitalized} (${formattedDate})`;
            
            boardData.cards.push({
                id: `card-${nextCardId++}`,
                title, 
                description, 
                column,
                createdAt: now,
                statusChanges: [{
                    from: null,
                    to: column,
                    timestamp: now
                }]
            });
        }
        
        saveToServer();
        renderBoard();
        closeModalFn();
    }

    function formatDate(isoString) {
        const date = new Date(isoString);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }

    function createCardElement(card) {
        console.log("Creating card element for:", JSON.stringify(card, null, 2));
        
        const template = document.getElementById('card-template');
        const cardElement = template.content.cloneNode(true).querySelector('.card');
        
        cardElement.dataset.id = card.id;
        cardElement.querySelector('.card-title').textContent = card.title;
        
        // Use the description directly as it now contains the timestamps
        cardElement.querySelector('.card-description').textContent = card.description;
        
        // If a card was created before our timestamp feature and is missing timestamps,
        // add them to the description when the card is loaded
        if (!card.description.includes("📅 Created:")) {
            const now = new Date().toISOString();
            const columnName = card.column.charAt(0).toUpperCase() + card.column.slice(1);
            
            // Initialize timestamps if they don't exist
            if (!card.createdAt) {
                card.createdAt = now;
            }
            
            if (!card.statusChanges || card.statusChanges.length === 0) {
                card.statusChanges = [{
                    from: null,
                    to: card.column,
                    timestamp: now
                }];
            }
            
            // Format the timestamps
            const createdTime = formatDate(card.createdAt);
            const lastChange = card.statusChanges[card.statusChanges.length - 1];
            const statusTime = formatDate(lastChange.timestamp);
            
            // Update the card description with timestamps
            card.description = `${card.description}\n\n📅 Created: ${createdTime}\n🔄 Status: ${columnName} (${statusTime})`;
            cardElement.querySelector('.card-description').textContent = card.description;
            
            // Save the updated card data
            saveToServer();
        }
        
        cardElement.querySelector('.edit-btn').addEventListener('click', () => openModal(card.id));
        cardElement.querySelector('.delete-btn').addEventListener('click', () => {
            if (confirm('Delete this card?')) {
                boardData.cards = boardData.cards.filter(c => c.id !== card.id);
                saveToServer();
                renderBoard();
            }
        });
        
        cardElement.addEventListener('dragstart', handleDragStart);
        cardElement.addEventListener('dragend', handleDragEnd);
        
        return cardElement;
    }

    function renderBoard() {
        cardContainers.forEach(container => container.innerHTML = '');
        boardData.cards.forEach(card => {
            const container = document.querySelector(`.card-container[data-column="${card.column}"]`);
            if (container) container.appendChild(createCardElement(card));
        });
    }

    function handleDragStart(e) {
        e.dataTransfer.setData('text/plain', e.target.dataset.id);
        e.target.classList.add('dragging');
        setTimeout(() => e.target.style.opacity = '0.4', 0);
    }

    function handleDragEnd(e) {
        e.target.classList.remove('dragging');
        e.target.style.opacity = '1';
        document.querySelectorAll('.card-container').forEach(c => c.classList.remove('drop-highlight'));
    }

    function handleDragOver(e) {
        e.preventDefault();
        this.classList.add('drop-highlight');
    }

    function handleDragLeave() {
        this.classList.remove('drop-highlight');
    }

    function formatDate(isoString) {
        const date = new Date(isoString);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }

    function handleDrop(e) {
        e.preventDefault();
        this.classList.remove('drop-highlight');
        
        const cardId = e.dataTransfer.getData('text/plain');
        const targetColumn = this.dataset.column;
        
        const cardIndex = boardData.cards.findIndex(c => c.id === cardId);
        if (cardIndex !== -1) {
            const oldColumn = boardData.cards[cardIndex].column;
            const nowTimestamp = new Date().toISOString();
            
            // Only track status change if the column actually changed
            if (oldColumn !== targetColumn) {
                // Initialize statusChanges array if it doesn't exist
                if (!boardData.cards[cardIndex].statusChanges) {
                    boardData.cards[cardIndex].statusChanges = [];
                }
                
                // Add the status change with current timestamp
                boardData.cards[cardIndex].statusChanges.push({
                    from: oldColumn,
                    to: targetColumn,
                    timestamp: nowTimestamp
                });
                
                // Get the capitalized target column name
                const targetColumnCapitalized = targetColumn.charAt(0).toUpperCase() + targetColumn.slice(1);
                const formattedDate = formatDate(nowTimestamp);
                
                // Extract the existing description before timestamps
                let description = boardData.cards[cardIndex].description;
                if (description.includes("📅 Created:")) {
                    description = description.split("📅 Created:")[0].trim();
                }
                
                // If there's no createdAt, add it now
                if (!boardData.cards[cardIndex].createdAt) {
                    boardData.cards[cardIndex].createdAt = nowTimestamp;
                }
                
                // Format the created time
                const createdDate = formatDate(boardData.cards[cardIndex].createdAt);
                
                // Update the description with new timestamps
                boardData.cards[cardIndex].description = 
                    `${description}\n\n📅 Created: ${createdDate}\n🔄 Status: ${targetColumnCapitalized} (${formattedDate})`;
            }
            
            boardData.cards[cardIndex].column = targetColumn;
            saveToServer();
            renderBoard();
        }
    }

    function exportToFile() {
        const blob = new Blob([JSON.stringify(boardData, null, 2)], {type: 'application/json'});
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'kanban-board.json';
        a.click();
    }

    function importFromFile(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                boardData = JSON.parse(e.target.result);
                updateNextCardId();
                saveToServer();
                renderBoard();
            } catch (err) {
                alert('Invalid file format');
            }
        };
        reader.readAsText(file);
    }
});