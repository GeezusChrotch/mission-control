#!/usr/bin/env node
/**
 * Migrate old kanban cards to Mission Control format
 */

const fs = require('fs');
const path = require('path');

const KANBAN_PATH = '/Users/Josh/clawd/kanban/kanban.json';
const TASKS_PATH = '/Users/Josh/clawd/data/tasks.json';

// Column mapping: old kanban → Mission Control
const COLUMN_MAP = {
  'done': 'done',
  'todo': 'backlog',
  'inprogress': 'in_progress',
  'suggestions': 'backlog',
  'permanent': 'permanent'
};

function migrateCard(card) {
  return {
    id: card.id,
    title: card.title,
    description: card.description,
    status: COLUMN_MAP[card.column] || 'backlog',
    project: card.id.startsWith('suggestion') ? 'suggestions' : 
             card.id.startsWith('idea') ? 'ideas' : 
             card.id.startsWith('guide') ? 'guides' : 'default',
    tags: card.id.startsWith('suggestion') ? ['suggestion'] : 
          card.id.startsWith('idea') ? ['idea'] : 
          card.id.startsWith('guide') ? ['guide'] : [],
    priority: 'medium',
    createdAt: card.createdAt,
    comments: [],
    subtasks: card.subtasks || []
  };
}

function main() {
  // Read old kanban
  const kanbanData = JSON.parse(fs.readFileSync(KANBAN_PATH, 'utf8'));
  
  // Read current tasks
  const tasksData = JSON.parse(fs.readFileSync(TASKS_PATH, 'utf8'));
  
  // Get existing task IDs to avoid duplicates
  const existingIds = new Set(tasksData.tasks.map(t => t.id));
  
  // Migrate cards that don't exist yet
  let migratedCount = 0;
  for (const card of kanbanData.cards) {
    if (!existingIds.has(card.id)) {
      const migrated = migrateCard(card);
      tasksData.tasks.push(migrated);
      existingIds.add(card.id);
      migratedCount++;
      console.log(`Migrated: ${card.id} - ${card.title}`);
    } else {
      console.log(`Skipped (exists): ${card.id}`);
    }
  }
  
  // Update projects if needed
  const existingProjects = new Set(tasksData.projects.map(p => p.id));
  if (!existingProjects.has('suggestions')) {
    tasksData.projects.push({ id: 'suggestions', name: 'Suggestions', color: '#8b5cf6', icon: '💡' });
  }
  if (!existingProjects.has('ideas')) {
    tasksData.projects.push({ id: 'ideas', name: 'Ideas', color: '#f59e0b', icon: '✨' });
  }
  
  // Update timestamp
  tasksData.lastUpdated = new Date().toISOString();
  
  // Write back
  fs.writeFileSync(TASKS_PATH, JSON.stringify(tasksData, null, 2));
  
  console.log(`\n✅ Migrated ${migratedCount} tasks`);
  console.log(`📊 Total tasks: ${tasksData.tasks.length}`);
}

main();
