import React, {useEffect, useRef} from 'react';
import {createPortal} from 'react-dom';
import {ArrowLeft, ArrowRight, Check, Info, Sparkles, X} from 'lucide-react';
import {tourSteps} from '../app/config.jsx';
import {AnimatedButton} from '../motion/components.jsx';
import {useReveal} from '../motion/hooks.js';

export function TourDialog({index, setIndex, onClose}) {
  const ref = useRef(null);
  const lastFocus = useRef(null);
  const step = tourSteps[index];
  useReveal(ref, index);

  useEffect(() => {
    lastFocus.current = document.activeElement;
    ref.current?.querySelector('button')?.focus();
    return () => lastFocus.current?.focus?.();
  }, []);

  useEffect(() => {
    ref.current?.querySelector('button')?.focus();
  }, [index]);

  const trap = event => {
    if (event.key === 'Escape') {
      event.preventDefault();
      onClose();
      return;
    }
    if (event.key !== 'Tab') return;
    const controls = [...ref.current.querySelectorAll('button:not(:disabled)')];
    if (!controls.length) return;
    const first = controls[0];
    const last = controls.at(-1);
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  };

  return createPortal(
    <div className="tour-scrim">
      <section
        ref={ref}
        onKeyDown={trap}
        tabIndex={-1}
        className="tour-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="tour-title"
        aria-describedby="tour-description"
      >
        <div className="tour-progress">
          <span>PRODUCT TOUR</span>
          <span className="tour-step-count" aria-label={`Step ${index + 1} of ${tourSteps.length}`}>
            {index + 1} <i>/ {tourSteps.length}</i>
          </span>
          <button className="tour-close" aria-label="Close product tour" onClick={onClose}>
            <X size={17}/>
          </button>
        </div>
        <div
          className="tour-progress-bar"
          role="progressbar"
          aria-label="Product tour progress"
          aria-valuemin={0}
          aria-valuemax={tourSteps.length}
          aria-valuenow={index + 1}
          aria-valuetext={`Step ${index + 1} of ${tourSteps.length}`}
        >
          <i style={{width: `${(index + 1) / tourSteps.length * 100}%`}}/>
        </div>
        <div className="tour-icon"><Sparkles size={20}/></div>
        <h2 id="tour-title">{step.title}</h2>
        <p id="tour-description">{step.body}</p>
        <span className="tour-tip"><Info size={14}/>{step.next}</span>
        <div className="tour-actions">
          <button className="tour-skip" onClick={onClose}>Skip tour</button>
          <div>
            {index > 0 && (
              <button className="button button-secondary" onClick={() => setIndex(index - 1)}>
                <ArrowLeft size={15}/> Previous
              </button>
            )}
            <AnimatedButton
              className="button button-primary"
              onClick={() => index === tourSteps.length - 1 ? onClose() : setIndex(index + 1)}
            >
              {index === tourSteps.length - 1 ? 'Finish' : 'Next'}
              {index === tourSteps.length - 1 ? <Check size={15}/> : <ArrowRight size={15}/>}
            </AnimatedButton>
          </div>
        </div>
      </section>
    </div>,
    document.body
  );
}
