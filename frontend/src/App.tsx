import { Routes, Route } from 'react-router-dom';
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import Dashboard from './pages/Dashboard';
import ProjectSettings from './pages/ProjectSettings';
import AssetGenerator from './pages/AssetGenerator';
import SpriteSheetTool from './pages/SpriteSheetTool';
import TilePreview from './pages/TilePreview';
import AssetGallery from './pages/AssetGallery';
import ExportPage from './pages/ExportPage';

export default function App() {
  return (
    <div className="flex flex-col h-screen">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-6 bg-gray-950">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/settings" element={<ProjectSettings />} />
            <Route path="/generator" element={<AssetGenerator />} />
            <Route path="/spritesheet" element={<SpriteSheetTool />} />
            <Route path="/tile" element={<TilePreview />} />
            <Route path="/assets" element={<AssetGallery />} />
            <Route path="/export" element={<ExportPage />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
