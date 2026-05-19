import 'dart:async';
import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ResultScreen extends StatefulWidget {
  final String jobId;
  const ResultScreen({super.key, required this.jobId});

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  final _api = ApiService();
  String _status = 'queued';
  int _progress = 0;
  String? _outputUrl;
  String? _error;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _poll();
    _timer = Timer.periodic(const Duration(seconds: 2), (_) => _poll());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _poll() async {
    try {
      final data = await _api.getJobStatus(widget.jobId);
      setState(() {
        _status   = data['status'];
        _progress = data['progress'];
        _outputUrl = data['output'];
        _error    = data['error'];
      });
      if (_status == 'done' || _status == 'failed') {
        _timer?.cancel();
      }
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Your Reel')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (_status != 'done' && _status != 'failed') ...[
              Text('Status: $_status',
                  style: Theme.of(context).textTheme.titleMedium,
                  textAlign: TextAlign.center),
              const SizedBox(height: 24),
              LinearProgressIndicator(value: _progress / 100),
              const SizedBox(height: 12),
              Text('$_progress%', textAlign: TextAlign.center),
            ],
            if (_status == 'done' && _outputUrl != null) ...[
              const Icon(Icons.check_circle, color: Colors.greenAccent, size: 64),
              const SizedBox(height: 16),
              const Text('Reel ready!',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.w600)),
              const SizedBox(height: 24),
              FilledButton.icon(
                icon: const Icon(Icons.download),
                label: const Text('Download Reel'),
                onPressed: () {
                  // open download URL
                  final url = '${ApiService.baseUrl}$_outputUrl';
                  // use url_launcher in production
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Video at: $url')),
                  );
                },
              ),
            ],
            if (_status == 'failed') ...[
              const Icon(Icons.error_outline, color: Colors.redAccent, size: 64),
              const SizedBox(height: 16),
              Text('Generation failed:\n${_error ?? "unknown error"}',
                  textAlign: TextAlign.center),
            ],
          ],
        ),
      ),
    );
  }
}
