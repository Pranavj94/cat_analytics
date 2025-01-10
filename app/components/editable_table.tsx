// import React, { useState, useEffect } from 'react';
// import { Input } from '@/components/ui/input';

// const EditableTable = ({ initialData = {} }) => {
//   const [data, setData] = useState({});

//   useEffect(() => {
//     setData(initialData);
//   }, [initialData]);

//   const handleChange = (key, value) => {
//     setData(prev => ({
//       ...prev,
//       [key]: value
//     }));
//   };

//   return (
//     <div className="overflow-x-auto rounded-md border">
//       <table className="w-full">
//         <thead className="bg-gray-100">
//           <tr>
//             <th className="h-12 px-4 text-left align-middle font-medium">Key</th>
//             <th className="h-12 px-4 text-left align-middle font-medium">Value</th>
//           </tr>
//         </thead>
//         <tbody>
//           {Object.entries(data).map(([key, value]) => (
//             <tr key={key} className="border-t hover:bg-gray-50">
//               <td className="p-4">{key}</td>
//               <td className="p-4">
//                 <Input 
//                   value={value}
//                   onChange={(e) => handleChange(key, e.target.value)}
//                 />
//               </td>
//             </tr>
//           ))}
//         </tbody>
//       </table>
//     </div>
//   );
// };

// export default EditableTable;