"use client";
import { useEffect, useState } from "react";
import Link from "next/link";

interface Asset {
  id: number;
  name: string;
  type: string;
  parent_id: number | null;
  org_id: number | null;
  capacity: number | null;
  status: string;
}

export default function AssetManagement() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Form states
  const [showForm, setShowForm] = useState(false);
  const [formType, setFormType] = useState("BUILDING"); // BUILDING, FLOOR, CLASSROOM, GROUND
  const [formName, setFormName] = useState("");
  const [formParentId, setFormParentId] = useState<number | "">("");
  const [formCapacity, setFormCapacity] = useState("");

  const fetchAssets = async () => {
    try {
      const res = await fetch("/api/asset/");
      const data = await res.json();
      setAssets(data);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssets();
  }, []);

  const handleAddAsset = async (e: React.FormEvent) => {
    e.preventDefault();
    await fetch("/api/asset/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: formName,
        type: formType,
        parent_id: formParentId ? Number(formParentId) : null,
        capacity: formCapacity ? Number(formCapacity) : null,
        org_id: 1 // Default Main Campus
      })
    });
    
    setShowForm(false);
    setFormName("");
    setFormParentId("");
    setFormCapacity("");
    fetchAssets();
  };

  // Helper to build hierarchy
  const getChildren = (parentId: number | null) => {
    return assets.filter(a => a.parent_id === parentId);
  };

  const renderAssetNode = (asset: Asset, depth: number = 0) => {
    const children = getChildren(asset.id);
    const marginLeft = depth * 32; // 32px per depth level
    
    // Icons based on type
    let icon = "📦";
    if (asset.type === "BUILDING") icon = "🏢";
    if (asset.type === "FLOOR") icon = "📶";
    if (asset.type === "CLASSROOM") icon = "🚪";
    if (asset.type === "GROUND") icon = "🌳";

    return (
      <div key={asset.id} className="w-full">
        <div 
          className="flex items-center justify-between p-3 border-b border-gray-100 hover:bg-gray-50 transition"
          style={{ paddingLeft: `${marginLeft + 16}px` }}
        >
          <div className="flex items-center gap-3">
            <span className="text-xl">{icon}</span>
            <div>
              <span className="font-semibold text-gray-900">{asset.name}</span>
              <span className="ml-3 text-xs font-bold text-gray-500 uppercase tracking-wider bg-gray-100 px-2 py-1 rounded">{asset.type}</span>
            </div>
          </div>
          <div className="flex items-center gap-6">
            {asset.capacity && <span className="text-sm text-gray-500">Cap: {asset.capacity}</span>}
            <span className="text-sm text-green-600 font-medium">● {asset.status}</span>
            <button 
              onClick={() => {
                setFormParentId(asset.id);
                setFormType(asset.type === "BUILDING" ? "FLOOR" : "CLASSROOM");
                setShowForm(true);
              }}
              className="text-sm text-blue-600 hover:underline"
            >
              + Add Sub-Asset
            </button>
          </div>
        </div>
        
        {/* Render children recursively */}
        {children.length > 0 && (
          <div className="border-l-2 border-gray-200 ml-4">
            {children.map(child => renderAssetNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  const rootAssets = getChildren(null);

  return (
    <div className="min-h-screen bg-gray-50 p-8 font-[family-name:var(--font-geist-sans)]">
      <div className="max-w-5xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Asset & Facilities Management</h1>
            <p className="text-gray-500 mt-1">Manage buildings, floors, classrooms, and grounds.</p>
          </div>
          <div className="flex gap-3">
            <button 
              onClick={() => { setFormParentId(""); setShowForm(true); setFormType("BUILDING"); }}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
            >
              + New Root Asset
            </button>
            <Link href="/dashboard?role=ADMIN" className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300">
              Back to Dashboard
            </Link>
          </div>
        </div>

        {/* Add Asset Form Modal */}
        {showForm && (
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8 animate-in fade-in slide-in-from-top-4">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Add New Asset</h2>
            <form onSubmit={handleAddAsset} className="flex items-end gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">Asset Type</label>
                <select 
                  value={formType} 
                  onChange={(e) => setFormType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="BUILDING">Building</option>
                  <option value="FLOOR">Floor</option>
                  <option value="CLASSROOM">Classroom</option>
                  <option value="GROUND">Ground</option>
                </select>
              </div>
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input 
                  type="text" 
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  required 
                  placeholder="e.g. Science Block"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" 
                />
              </div>
              
              {formType === "CLASSROOM" && (
                <div className="w-32">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Capacity</label>
                  <input 
                    type="number" 
                    value={formCapacity}
                    onChange={(e) => setFormCapacity(e.target.value)}
                    placeholder="e.g. 30"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" 
                  />
                </div>
              )}
              
              <div className="flex gap-2">
                <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">Save Asset</button>
              </div>
            </form>
          </div>
        )}

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="p-8 text-center text-gray-500">Loading infrastructure...</div>
          ) : rootAssets.length === 0 ? (
            <div className="p-8 text-center text-gray-500">No assets found. Click 'New Root Asset' to create a Building or Ground.</div>
          ) : (
            <div className="divide-y divide-gray-100">
              {rootAssets.map(asset => renderAssetNode(asset))}
            </div>
          )}
        </div>
        
      </div>
    </div>
  );
}
