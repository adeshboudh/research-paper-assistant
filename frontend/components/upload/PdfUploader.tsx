'use client';

import { useState, useRef } from 'react';
import { Upload, FileText, Loader2, CheckCircle, XCircle } from 'lucide-react';
import { uploadPdf } from '@/lib/api';

export default function PdfUploader() {
    const [file, setFile] = useState<File | null>(null);
    const [title, setTitle] = useState('');
    const [authors, setAuthors] = useState('');
    const [year, setYear] = useState('');
    const [isUploading, setIsUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
    const [message, setMessage] = useState('');
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0];
            if (selectedFile.type === 'application/pdf') {
                setFile(selectedFile);
                setUploadStatus('idle');
                // Auto-fill title from filename
                if (!title) {
                    setTitle(selectedFile.name.replace('.pdf', ''));
                }
            } else {
                setMessage('Please select a PDF file');
                setUploadStatus('error');
            }
        }
    };

    const handleUpload = async () => {
        if (!file || !title) {
            setMessage('Please provide a file and title');
            setUploadStatus('error');
            return;
        }

        setIsUploading(true);
        setUploadStatus('idle');

        try {
            const result = await uploadPdf(
                file,
                title,
                authors || undefined,
                year ? parseInt(year) : undefined
            );

            setMessage(`Successfully uploaded! ${result.chunks_indexed} chunks indexed.`);
            setUploadStatus('success');

            // Reset form
            setTimeout(() => {
                setFile(null);
                setTitle('');
                setAuthors('');
                setYear('');
                setUploadStatus('idle');
                if (fileInputRef.current) {
                    fileInputRef.current.value = '';
                }
            }, 3000);
        } catch (error: any) {
            setMessage(`Upload failed: ${error.response?.data?.message || error.message}`);
            setUploadStatus('error');
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
            <div className="flex items-center gap-3 mb-6">
                <Upload className="text-blue-600" size={24} />
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Upload Research Paper
                </h2>
            </div>

            {/* File Upload */}
            <div className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        PDF File *
                    </label>
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept=".pdf"
                        onChange={handleFileChange}
                        className="block w-full text-sm text-gray-900 dark:text-gray-100 border border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer bg-gray-50 dark:bg-gray-700 focus:outline-none"
                    />
                    {file && (
                        <div className="mt-2 flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                            <FileText size={16} />
                            <span>{file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                        </div>
                    )}
                </div>

                {/* Title */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Paper Title *
                    </label>
                    <input
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="Enter paper title"
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                    />
                </div>

                {/* Authors */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Authors (optional)
                    </label>
                    <input
                        type="text"
                        value={authors}
                        onChange={(e) => setAuthors(e.target.value)}
                        placeholder="e.g., John Doe, Jane Smith"
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                    />
                </div>

                {/* Year */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Publication Year (optional)
                    </label>
                    <input
                        type="number"
                        value={year}
                        onChange={(e) => setYear(e.target.value)}
                        placeholder="2024"
                        min="1900"
                        max={new Date().getFullYear()}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                    />
                </div>

                {/* Upload Button */}
                <button
                    onClick={handleUpload}
                    disabled={!file || !title || isUploading}
                    className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                    {isUploading ? (
                        <>
                            <Loader2 size={20} className="animate-spin" />
                            <span>Uploading...</span>
                        </>
                    ) : (
                        <>
                            <Upload size={20} />
                            <span>Upload and Process</span>
                        </>
                    )}
                </button>

                {/* Status Message */}
                {message && (
                    <div
                        className={`flex items-center gap-2 p-3 rounded-lg ${uploadStatus === 'success'
                                ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-300'
                                : uploadStatus === 'error'
                                    ? 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-300'
                                    : ''
                            }`}
                    >
                        {uploadStatus === 'success' && <CheckCircle size={20} />}
                        {uploadStatus === 'error' && <XCircle size={20} />}
                        <span className="text-sm">{message}</span>
                    </div>
                )}
            </div>
        </div>
    );
}