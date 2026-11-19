import React from 'react';
import {createRoot} from 'react-dom/client';
import {App} from './src/app/App.jsx';
import './src/styles/legacy.css';
import './src/styles/theme.css';
import './src/styles/tour.css';
import './src/motion/motion.css';
createRoot(document.getElementById('root')).render(<App/>);
