#!/bin/bash
# habit-tracker.sh - Daily goal & habit tracker with streaks
# Usage: ./habit-tracker.sh <command> [args]
# Commands: add <habit>, list, done <habit>, streak <habit>, reset

set -e

# Set PATH for cron
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:/Users/Josh/.bun/bin"

HABITS_FILE="$HOME/.habits.json"
TODAY=$(date +"%Y-%m-%d")

# Initialize habits file if needed
init_habits() {
    if [ ! -f "$HABITS_FILE" ]; then
        echo '{"habits": [],"history": {}}' > "$HABITS_FILE"
    fi
}

# Add a new habit
add_habit() {
    local name="$1"
    if [ -z "$name" ]; then
        echo "Usage: ./habit-tracker.sh add <habit name>"
        exit 1
    fi

    init_habits

    # Check if already exists
    local exists=$(node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('$HABITS_FILE', 'utf8'));
console.log(data.habits.find(h => h.name.toLowerCase() === '$name'.toLowerCase()) ? 'yes' : 'no');
" 2>/dev/null || echo "no")

    if [ "$exists" = "yes" ]; then
        echo "Habit '$name' already exists!"
        exit 1
    fi

    node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('$HABITS_FILE', 'utf8'));
data.habits.push({
    name: '$name',
    created: '$TODAY',
    streak: 0,
    lastCompleted: null
});
fs.writeFileSync('$HABITS_FILE', JSON.stringify(data, null, 2));
"
    echo "✅ Added habit: $name"
}

# List all habits with progress
list_habits() {
    init_habits

    echo "🎯 HABITS & GOALS ($TODAY)"
    echo "============================"

    node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('$HABITS_FILE', 'utf8'));
const today = '$TODAY';

if (data.habits.length === 0) {
    console.log('No habits yet. Add one with: ./habit-tracker.sh add <habit>');
    process.exit(0);
}

data.habits.forEach(h => {
    // Check if done today
    const doneToday = h.lastCompleted === today;
    const status = doneToday ? '✅' : '⬜';
    const streakStr = h.streak > 0 ? ' 🔥 ' + h.streak + ' day streak' : '';
    console.log(status + ' ' + h.name + streakStr);
});
console.log('');
console.log('============================');
console.log('Use: ./habit-tracker.sh done <habit>');
"

    # Show recent completions from history
    echo ""
    echo "📊 Recent completions:"
    node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('$HABITS_FILE', 'utf8'));
const history = data.history || {};
const dates = Object.keys(history).sort().reverse().slice(0, 5);
dates.forEach(d => {
    const count = history[d] || 0;
    console.log('  ' + d + ': ' + count + ' completed');
});
" 2>/dev/null || echo "  No history yet"
}

# Mark a habit as done today
done_habit() {
    local name="$1"
    if [ -z "$name" ]; then
        echo "Usage: ./habit-tracker.sh done <habit>"
        exit 1
    fi

    init_habits

    node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('$HABITS_FILE', 'utf8'));
const today = '$TODAY';
const habit = data.habits.find(h => h.name.toLowerCase() === '$name'.toLowerCase());

if (!habit) {
    console.log('Habit not found: $name');
    process.exit(1);
}

if (habit.lastCompleted === today) {
    console.log('Already completed today: ' + habit.name);
    process.exit(0);
}

// Update streak
const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
if (habit.lastCompleted === yesterday) {
    habit.streak += 1;
} else {
    habit.streak = 1;
}
habit.lastCompleted = today;

// Update history
if (!data.history) data.history = {};
data.history[today] = (data.history[today] || 0) + 1;

fs.writeFileSync('$HABITS_FILE', JSON.stringify(data, null, 2));
console.log('✅ ' + habit.name + ' - Streak: ' + habit.streak);
"
}

# Show streak for a habit
show_streak() {
    local name="$1"
    if [ -z "$name" ]; then
        echo "Usage: ./habit-tracker.sh streak <habit>"
        exit 1
    fi

    init_habits

    node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('$HABITS_FILE', 'utf8'));
const habit = data.habits.find(h => h.name.toLowerCase() === '$name'.toLowerCase());

if (!habit) {
    console.log('Habit not found: $name');
    process.exit(1);
}

console.log(habit.name + ': ' + habit.streak + ' day streak');
console.log('Last completed: ' + (habit.lastCompleted || 'Never'));
"
}

# Show progress visualization
progress() {
    init_habits

    echo "📈 STREAK VISUALIZATION"
    echo "========================"

    node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('$HABITS_FILE', 'utf8'));
const history = data.history || {};
const today = '$TODAY';

// Show last 7 days
for (let i = 6; i >= 0; i--) {
    const d = new Date(Date.now() - i * 86400000).toISOString().split('T')[0];
    const count = history[d] || 0;
    const bar = '█'.repeat(Math.min(count, 10)) + '░'.repeat(10 - Math.min(count, 10));
    const mark = d === today ? '●' : '○';
    console.log(mark + ' ' + d + ' [' + bar + '] ' + count);
}
"
}

# Reset today's progress (for testing)
reset_today() {
    init_habits

    node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('$HABITS_FILE', 'utf8'));
const today = '$TODAY';

// Reset lastCompleted for today
data.habits.forEach(h => {
    if (h.lastCompleted === today) {
        h.lastCompleted = null;
        h.streak = Math.max(0, h.streak - 1);
    }
});

// Remove from history
if (data.history && data.history[today]) {
    delete data.history[today];
}

fs.writeFileSync('$HABITS_FILE', JSON.stringify(data, null, 2));
console.log('Reset today\\'s progress');
"
}

# Main command router
case "${1:-list}" in
    add) add_habit "$2" ;;
    list) list_habits ;;
    done|check) done_habit "$2" ;;
    streak) show_streak "$2" ;;
    progress) progress ;;
    reset) reset_today ;;
    help)
        echo "Habit Tracker Commands:"
        echo "  ./habit-tracker.sh add <name>    - Add new habit"
        echo "  ./habit-tracker.sh list          - Show all habits"
        echo "  ./habit-tracker.sh done <name>   - Mark habit complete today"
        echo "  ./habit-tracker.sh streak <name> - Show streak for habit"
        echo "  ./habit-tracker.sh progress      - Visual progress (7 days)"
        echo "  ./habit-tracker.sh reset         - Reset today's progress"
        ;;
    *) list_habits ;;
esac