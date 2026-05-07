/**
 * Review history feed — renders a list of ReviewCard components.
 */

import { ReviewCard, Review } from './ReviewCard';

interface ReviewFeedProps {
  reviews: Review[];
}

export function ReviewFeed({ reviews }: ReviewFeedProps) {
  if (reviews.length === 0) {
    return (
      <div className="text-center py-14 text-slate-400">
        <p className="text-sm">No reviews yet.</p>
        <p className="text-xs mt-1">Push code to a connected repository to trigger a review.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {reviews.map((r, i) => (
        <ReviewCard key={`${r.commit_sha}-${i}`} review={r} />
      ))}
    </div>
  );
}
