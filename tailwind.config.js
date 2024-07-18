/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./admin/src/**/*.html", "node_modules/preline/dist/*.js"],
    theme: {
      extend: {},
    },
    daisyui: {
      themes: [
        {
          mytheme: {
                    
          "primary": "#009485",
                    
          "secondary": "#8b5cf6",
                    
          "accent": "#22d3ee",
                    
          "neutral": "#a855f7",
                    
          "base-100": "#ffffff",
                    
          "info": "#4ade80",
                    
          "success": "#448aff",
                    
          "warning": "#ffa65c",
                    
          "error": "#ff0000",
          },
        },
      ],
    },
    plugins: [
      require('daisyui'),
      require('tailwindcss-animated'),
    ],
  }