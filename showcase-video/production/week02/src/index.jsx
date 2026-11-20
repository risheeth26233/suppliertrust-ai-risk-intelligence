import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {SupplierTrustFilm} from './film.jsx';

const Root = () => <Composition id="SupplierTrustWeek02" component={SupplierTrustFilm} durationInFrames={3600} fps={30} width={1920} height={1080} />;
registerRoot(Root);
