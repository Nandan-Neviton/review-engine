'use client';

import { useEffect, useState } from 'react';

interface FileChanged {
  filename: string;
  status: string;
  additions: number;
  deletions: number;
  changes: number;
  patch: string;
}

interface ReviewData {
  status: string;
  repository: string;
  branch: string;
  author: string;
  commit_sha: string;
  total_files_changed: number;
  files_changed: FileChanged[];
}

export default function ReviewDashboard() {
  const [review, setReview] = useState<ReviewData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('https://review-engine.onrender.com/')
      .then((res) => {
        if (!res.ok) throw new Error(`Server error: ${res.status}`);
        return res.json();
      })
      .then((data: ReviewData) => {
        setReview(data);
      })
      .catch((err) => {
        setError(err.message || 'Failed to connect to the review server.');
      });
  }, []);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center text-red-600 text-xl font-semibold">
        {error}
      </div>
    );
  }

  if (!review || !review.files_changed) {
    return (
      <div className="min-h-screen flex items-center justify-center text-2xl font-semibold">
        Waiting for review data...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-6xl mx-auto space-y-6">

        <div className="bg-white rounded-3xl shadow-xl p-8 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900">
                AI Review Pipeline
              </h1>

              <p className="text-gray-500 mt-2">
                Live GitHub Review Output
              </p>
            </div>

            <div className="bg-green-100 text-green-700 px-4 py-2 rounded-full font-semibold">
              {review.status.toUpperCase()}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

          <div className="bg-white rounded-3xl shadow-lg p-6 border border-gray-200">
            <h2 className="text-xl font-semibold mb-4">
              Repository Information
            </h2>

            <div className="space-y-3">

              <div>
                <span className="font-semibold">Repository:</span>
                <p className="text-gray-600 break-all">
                  {review.repository}
                </p>
              </div>

              <div>
                <span className="font-semibold">Branch:</span>
                <p className="text-gray-600">
                  {review.branch}
                </p>
              </div>

              <div>
                <span className="font-semibold">Author:</span>
                <p className="text-gray-600">
                  {review.author}
                </p>
              </div>

              <div>
                <span className="font-semibold">Commit SHA:</span>
                <p className="text-gray-600 break-all font-mono text-xs">
                  {review.commit_sha}
                </p>
              </div>

            </div>
          </div>

          <div className="bg-white rounded-3xl shadow-lg p-6 border border-gray-200">

            <h2 className="text-xl font-semibold mb-4">
              Review Summary
            </h2>

            <div className="grid grid-cols-2 gap-4">

              <div className="bg-blue-50 rounded-2xl p-4 border border-blue-100">
                <p className="text-sm text-blue-600 font-medium">
                  Files Changed
                </p>

                <p className="text-3xl font-bold text-blue-900 mt-2">
                  {review.total_files_changed}
                </p>
              </div>

              <div className="bg-purple-50 rounded-2xl p-4 border border-purple-100">
                <p className="text-sm text-purple-600 font-medium">
                  Total Changes
                </p>

                <p className="text-3xl font-bold text-purple-900 mt-2">
                  {review.files_changed.reduce(
                    (acc: number, file: FileChanged) => acc + file.changes,
                    0
                  )}
                </p>
              </div>

            </div>
          </div>
        </div>

        {review.files_changed.map((file: FileChanged, index: number) => (
          <div
            key={index}
            className="bg-white rounded-3xl shadow-xl border border-gray-200 overflow-hidden"
          >

            <div className="border-b border-gray-200 p-6 flex items-center justify-between bg-gray-50">

              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  {file.filename}
                </h2>

                <p className="text-sm text-gray-500 mt-1">
                  Status: {file.status}
                </p>
              </div>

              <div className="flex gap-3 text-sm">

                <div className="bg-green-100 text-green-700 px-3 py-1 rounded-full font-medium">
                  +{file.additions}
                </div>

                <div className="bg-red-100 text-red-700 px-3 py-1 rounded-full font-medium">
                  -{file.deletions}
                </div>

              </div>
            </div>

            <div className="p-6">

              <h3 className="font-semibold text-gray-800 mb-4">
                Git Diff Patch
              </h3>

              <pre className="bg-gray-950 text-green-400 p-6 rounded-2xl overflow-x-auto text-sm leading-6 whitespace-pre-wrap">
                {file.patch}
              </pre>

            </div>
          </div>
        ))}

      </div>
    </div>
  );
}