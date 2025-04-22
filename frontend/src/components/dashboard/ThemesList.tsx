import React from 'react';
import Badge from '../common/Badge';

interface ThemesListProps {
  themes: string[];
}

const ThemesList: React.FC<ThemesListProps> = ({ themes }) => {
  if (!themes || themes.length === 0) {
    return null;
  }

  // Rotate through different badge variants for visual variety
  const getBadgeVariant = (index: number) => {
    const variants: Array<'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'default'> = 
      ['primary', 'secondary', 'success', 'warning', 'error', 'default'];
    return variants[index % variants.length];
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-gray-900">Key Themes</h3>
      <div className="flex flex-wrap gap-2">
        {themes.map((theme, index) => (
          <Badge 
            key={index} 
            variant={getBadgeVariant(index)}
            className="mb-2 transition-all duration-300 transform hover:scale-110 cursor-pointer"
          >
            {theme}
          </Badge>
        ))}
      </div>
    </div>
  );
};

export default ThemesList;