
import React, { useState } from 'react';

const EditorPage = () => {
  const [content, setContent] = useState('');

  const handleChange = (event) => {
    setContent(event.target.value);
  };

  const handleSave = () => {
    console.log('Page content saved:', content);
  };

  return (
    <div>
      <h2>Editor</h2>
      <textarea value={content} onChange={handleChange} placeholder="Edit your page content..."></textarea>
      <button onClick={handleSave}>Save</button>
    </div>
  );
};

export default EditorPage;
