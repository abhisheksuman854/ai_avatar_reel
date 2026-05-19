import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../services/api_service.dart';
import 'result_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String? _imagePath, _imageFilename;
  String? _audioPath, _audioFilename;
  String _style = 'cinematic';
  String _engine = 'wav2lip';
  bool _loading = false;

  final _api = ApiService();
  final _styles = ['cinematic', 'hype', 'sad'];
  final _engines = ['wav2lip', 'sadtalker'];

  Future<void> _pickImage() async {
    final result = await FilePicker.platform.pickFiles(type: FileType.image);
    if (result != null) {
      final upload = await _api.uploadImage(result.files.single.path!);
      setState(() {
        _imagePath = result.files.single.path;
        _imageFilename = upload['filename'];
      });
    }
  }

  Future<void> _pickAudio() async {
    final result = await FilePicker.platform.pickFiles(type: FileType.audio);
    if (result != null) {
      final upload = await _api.uploadAudio(result.files.single.path!);
      setState(() {
        _audioPath = result.files.single.path;
        _audioFilename = upload['filename'];
      });
    }
  }

  Future<void> _generate() async {
    if (_imageFilename == null || _audioFilename == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Upload both an image and audio first')),
      );
      return;
    }
    setState(() => _loading = true);
    try {
      final jobId = await _api.generateReel(
        imageFilename: _imageFilename!,
        audioFilename: _audioFilename!,
        style: _style,
        engine: _engine,
      );
      if (mounted) {
        Navigator.push(context, MaterialPageRoute(
          builder: (_) => ResultScreen(jobId: jobId),
        ));
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Avatar Reel Generator'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _UploadCard(
              label: 'Avatar Image',
              icon: Icons.face,
              selected: _imagePath != null,
              subtitle: _imagePath != null ? 'Image ready ✓' : 'PNG / JPG',
              onTap: _pickImage,
            ),
            const SizedBox(height: 16),
            _UploadCard(
              label: 'Audio / Song',
              icon: Icons.music_note,
              selected: _audioPath != null,
              subtitle: _audioPath != null ? 'Audio ready ✓' : 'MP3 / WAV',
              onTap: _pickAudio,
            ),
            const SizedBox(height: 24),
            Text('Style', style: Theme.of(context).textTheme.labelLarge),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: _styles.map((s) => ChoiceChip(
                label: Text(s),
                selected: _style == s,
                onSelected: (_) => setState(() => _style = s),
              )).toList(),
            ),
            const SizedBox(height: 16),
            Text('Engine', style: Theme.of(context).textTheme.labelLarge),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: _engines.map((e) => ChoiceChip(
                label: Text(e),
                selected: _engine == e,
                onSelected: (_) => setState(() => _engine = e),
              )).toList(),
            ),
            const SizedBox(height: 32),
            FilledButton.icon(
              icon: _loading
                  ? const SizedBox(width: 18, height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Icon(Icons.auto_awesome),
              label: Text(_loading ? 'Generating…' : 'Generate Reel'),
              onPressed: _loading ? null : _generate,
              style: FilledButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 18),
                textStyle: const TextStyle(fontSize: 16),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _UploadCard extends StatelessWidget {
  final String label, subtitle;
  final IconData icon;
  final bool selected;
  final VoidCallback onTap;
  const _UploadCard({
    required this.label, required this.subtitle, required this.icon,
    required this.selected, required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: selected ? Theme.of(context).colorScheme.primary : Colors.white24,
          width: selected ? 1.5 : 0.5,
        ),
      ),
      child: ListTile(
        leading: Icon(icon, color: selected
            ? Theme.of(context).colorScheme.primary
            : Colors.white54),
        title: Text(label),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.upload_file),
        onTap: onTap,
      ),
    );
  }
}
