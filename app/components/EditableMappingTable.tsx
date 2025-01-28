const EditableMappingTable = ({ mapping, setMapping }: { 
  mapping: Record<string, string>, 
  setMapping: (mapping: Record<string, string>) => void 
}) => {
  const handleMappingChange = (original: string, newValue: string) => {
    setMapping({
      ...mapping,
      [original]: newValue
    });
  };
  
  return (
    <div className="bg-gray-50 p-4 mb-4 rounded-lg shadow-sm">
      <h3 className="font-semibold text-lg mb-2">Column Mappings:</h3>
      <div className="grid grid-cols-2 gap-4">
        {Object.entries(mapping).map(([original, mapped]) => (
          <div key={original} className="flex justify-between p-2 bg-white rounded border border-gray-200">
            <span className="text-gray-600">{original}</span>
            <span className="text-blue-600 font-medium">→</span>
            <input
              type="text"
              value={String(mapped)}
              onChange={(e) => handleMappingChange(original, e.target.value)}
              className="text-gray-800 font-medium border rounded px-2"
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default EditableMappingTable;

