import { Star } from 'lucide-react';
import clsx from 'clsx';

interface StarRatingProps {
  rating: number;
  maxRating?: number;
  size?: 'sm' | 'md' | 'lg';
  showValue?: boolean;
}

const sizeMap = {
  sm: 14,
  md: 18,
  lg: 22,
};

export default function StarRating({
  rating,
  maxRating = 5,
  size = 'md',
  showValue = true,
}: StarRatingProps) {
  const starSize = sizeMap[size];
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;

  return (
    <div className="flex items-center gap-1">
      {Array.from({ length: maxRating }, (_, index) => {
        const isFilled = index < fullStars;
        const isHalf = index === fullStars && hasHalfStar;

        return (
          <Star
            key={index}
            size={starSize}
            className={clsx(
              'transition-colors',
              isFilled || isHalf ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'
            )}
          />
        );
      })}
      {showValue && (
        <span className="ml-1 text-sm font-medium text-gray-600">
          {rating.toFixed(1)}
        </span>
      )}
    </div>
  );
}
