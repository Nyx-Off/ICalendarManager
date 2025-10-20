/**
 * ICalendar Manager - Frontend Application
 * @author Samy Bensalem
 */

class CalendarApp {
    constructor() {
        this.currentWeekOffset = 0;
        this.loadingElement = document.getElementById('loadingSpinner');
        this.errorElement = document.getElementById('errorMessage');
        this.calendarContainer = document.getElementById('calendarContainer');
        this.noEventsElement = document.getElementById('noEvents');
        this.currentWeekTitle = document.getElementById('currentWeekTitle');
        this.weekDates = document.getElementById('weekDates');
        this.lastUpdateElement = document.getElementById('lastUpdate');
        this.daysOfWeek = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];
        this.monthsOfYear = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];
        this.init();
    }
    
    init() {
        // Initialiser le dark mode
        this.initDarkMode();
        
        // Event listeners
        document.getElementById('prevWeek').addEventListener('click', () => this.changeWeek(-1));
        document.getElementById('nextWeek').addEventListener('click', () => this.changeWeek(1));
        document.getElementById('todayBtn').addEventListener('click', () => this.goToToday());
        document.getElementById('refreshBtn').addEventListener('click', () => this.refresh());
        
        this.loadEvents();
    }
    
    initDarkMode() {
        const darkModeToggle = document.getElementById('darkModeToggle');
        
        // Vérifier la préférence sauvegardée
        const savedMode = localStorage.getItem('darkMode');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedMode !== null) {
            const isDark = savedMode === 'true';
            this.setDarkMode(isDark);
        } else if (prefersDark) {
            this.setDarkMode(true);
        }
        
        // Event listener pour le bouton
        darkModeToggle.addEventListener('click', () => {
            const isDarkNow = document.documentElement.classList.contains('dark-mode');
            this.setDarkMode(!isDarkNow);
        });
    }
    
    setDarkMode(isDark) {
        if (isDark) {
            document.documentElement.classList.add('dark-mode');
            document.body.classList.add('dark-mode');
            document.getElementById('darkModeToggle').textContent = '☀️';
        } else {
            document.documentElement.classList.remove('dark-mode');
            document.body.classList.remove('dark-mode');
            document.getElementById('darkModeToggle').textContent = '🌙';
        }
        localStorage.setItem('darkMode', isDark);
    }
    
    changeWeek(offset) {
        this.currentWeekOffset += offset;
        this.loadEvents();
    }
    
    goToToday() {
        this.currentWeekOffset = 0;
        this.loadEvents();
    }
    
    async refresh() {
        try {
            this.showLoading();
            const response = await fetch('api/download_calendar.php');
            const data = await response.json();
            if (!data.success) {
                throw new Error(data.error || 'Erreur lors du téléchargement');
            }
            await this.loadEvents();
        } catch (error) {
            this.showError('Erreur lors de l\'actualisation : ' + error.message);
        }
    }
    
    async loadEvents() {
        try {
            this.showLoading();
            this.hideError();
            const response = await fetch(`api/get_events.php?week=${this.currentWeekOffset}`);
            const result = await response.json();
            if (!result.success) {
                throw new Error(result.error || 'Erreur inconnue');
            }
            this.displayEvents(result.data);
        } catch (error) {
            this.showError('Impossible de charger les événements : ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    displayEvents(data) {
        const { events, weekStart, weekEnd, weekNumber, year, lastUpdate } = data;
        this.updateWeekTitle(weekStart, weekEnd, weekNumber, year);
        if (lastUpdate) {
            this.lastUpdateElement.textContent = this.formatDateTime(lastUpdate);
        }
        this.calendarContainer.innerHTML = '';
        if (!events || Object.keys(events).length === 0) {
            this.noEventsElement.style.display = 'block';
            return;
        }
        this.noEventsElement.style.display = 'none';
        const startDate = new Date(weekStart);
        const allDays = [];
        for (let i = 0; i < 7; i++) {
            const currentDate = new Date(startDate);
            currentDate.setDate(startDate.getDate() + i);
            allDays.push(currentDate);
        }
        allDays.forEach(date => {
            const dateKey = this.formatDate(date);
            const dayEvents = events[dateKey] || [];
            if (dayEvents.length > 0) {
                const daySection = this.createDaySection(date, dayEvents);
                this.calendarContainer.appendChild(daySection);
            }
        });
    }
    
    createDaySection(date, events) {
        const section = document.createElement('div');
        section.className = 'day-section';
        const isToday = this.isToday(date);
        const header = document.createElement('div');
        header.className = `day-header${isToday ? ' today' : ''}`;
        const dayName = this.daysOfWeek[date.getDay()];
        const day = date.getDate();
        const month = this.monthsOfYear[date.getMonth()];
        header.innerHTML = `📅 ${dayName} ${day} ${month}${isToday ? ' <span class="today-badge">Aujourd\'hui</span>' : ''}`;
        section.appendChild(header);
        const eventsContainer = document.createElement('div');
        eventsContainer.className = 'day-events';
        events.forEach(event => {
            const eventCard = this.createEventCard(event);
            eventsContainer.appendChild(eventCard);
        });
        section.appendChild(eventsContainer);
        return section;
    }
    
    createEventCard(event) {
        const card = document.createElement('div');
        card.className = 'event-card';
        const header = document.createElement('div');
        header.className = 'event-header';
        const title = document.createElement('div');
        title.className = 'event-title';
        title.textContent = event.summary;
        const time = document.createElement('div');
        time.className = 'event-time';
        time.innerHTML = `⏰ ${event.startTime} - ${event.endTime}`;
        header.appendChild(title);
        header.appendChild(time);
        card.appendChild(header);
        if (event.location || event.description) {
            const details = document.createElement('div');
            details.className = 'event-details';
            if (event.location) {
                const location = document.createElement('div');
                location.className = 'event-location';
                location.innerHTML = `📍 ${this.escapeHtml(event.location)}`;
                details.appendChild(location);
            }
            if (event.description) {
                const description = document.createElement('div');
                description.className = 'event-description';
                description.innerHTML = `📝 ${this.escapeHtml(event.description)}`;
                details.appendChild(description);
            }
            card.appendChild(details);
        }
        return card;
    }
    
    updateWeekTitle(weekStart, weekEnd, weekNumber, year) {
        const start = new Date(weekStart);
        const end = new Date(weekEnd);
        this.currentWeekTitle.textContent = `Semaine ${weekNumber} - ${year}`;
        const startDay = start.getDate();
        const startMonth = this.monthsOfYear[start.getMonth()];
        const endDay = end.getDate();
        const endMonth = this.monthsOfYear[end.getMonth()];
        if (start.getMonth() === end.getMonth()) {
            this.weekDates.textContent = `${startDay} - ${endDay} ${endMonth} ${year}`;
        } else {
            this.weekDates.textContent = `${startDay} ${startMonth} - ${endDay} ${endMonth} ${year}`;
        }
    }
    
    formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
    
    formatDateTime(dateTimeString) {
        const date = new Date(dateTimeString);
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${day}/${month}/${year} à ${hours}:${minutes}`;
    }
    
    isToday(date) {
        const today = new Date();
        return date.getDate() === today.getDate() && date.getMonth() === today.getMonth() && date.getFullYear() === today.getFullYear();
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showLoading() {
        this.loadingElement.style.display = 'block';
        this.calendarContainer.style.display = 'none';
        this.noEventsElement.style.display = 'none';
    }
    
    hideLoading() {
        this.loadingElement.style.display = 'none';
        this.calendarContainer.style.display = 'block';
    }
    
    showError(message) {
        this.errorElement.textContent = '❌ ' + message;
        this.errorElement.style.display = 'block';
    }
    
    hideError() {
        this.errorElement.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new CalendarApp();
});