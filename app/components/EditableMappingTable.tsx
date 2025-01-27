

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
      };

export default EditableMappingTable;
    