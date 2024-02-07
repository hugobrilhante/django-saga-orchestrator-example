export const metadata = {
  title: "Microservices",
  description: "Implements orchestration-based sagas",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
