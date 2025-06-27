import QueryResult from '@/components/QueryResult';
import Sidebar from '@/components/Sidebar';
import Navbar from '@/components/Navbar';

export default function YourPage() {
  return (
    <div className="flex flex-col h-screen">
      {/* Navbar at the top */}
      <Navbar />
      
      <div className="flex flex-1">
        {/* Sidebar on the left */}
        <Sidebar />
        
        {/* Main content */}
        <main className="flex-1 overflow-auto">
          <QueryResult />
          {/* Your other content */}
        </main>
      </div>
    </div>
  );
}