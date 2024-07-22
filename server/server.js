const express = require('express');
const multer = require('multer');
const path = require('path');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.use(express.static('public'));

app.post('/api/upload-geotiff', upload.single('geotiff'), (req, res) => {
  console.log('Received upload request');
  if (req.file) {
    console.log('File uploaded:', req.file);
    res.json({
      id: path.basename(req.file.path),
      filename: req.file.originalname
    });
  } else {
    console.log('No file received');
    res.status(400).json({ error: 'No file uploaded' });
  }
});

app.get('/uploads/:id', (req, res) => {
  const filePath = path.join(__dirname, 'uploads', req.params.id);
  res.sendFile(filePath);
});

app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({ error: 'Internal server error', details: err.message });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));